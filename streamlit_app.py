import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import io
st.set_page_config(layout="wide")


@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

st.header('IVS-10238 - Finding Project Sectors FY23')

with st.expander('About this app'):
    st.markdown('''This streamlit is meant to visualize the effects of how we are assigning projects to sectors. 
                We used the sector coded to each indicator to rank each sector over a project (The sector with the most indicators gets ranked 1, the second most ranked 2, etc).
                From there, we used some logic to assign the sector to one of the major 5 sectors.
                The source code for this app and input data can be found at   
                   "Shared - IVS/3. Management/Data Quality Control/Data Cleaning/FY23 Cleaning/Project Sectors/WVC-10238-Project-Sectors-FY23"
                or at [this link](https://worldvisioncanada.sharepoint.com/:f:/r/sites/ImpactHub2/Shared%20Documents/3.%20Management/Data%20Quality%20Control/Data%20Cleaning/FY23%20Cleaning/Project%20Sectors/WVC-10238-Project-Sectors-FY23?csf=1&web=1&e=ozJNNl)
                ''')
    st.write('Written by Timmy Bender - last updated Jan 22, 2024')


## sidebar

type_options = ['GNT', 'PNS','GIK','SPN','WFP','OTH', 'All']
selected_type = st.sidebar.selectbox("Choose a Project Type to get started", options=type_options)

## Project Sectors

proj_df = pd.read_excel('./ProjectSectors.xlsx')
# proj_df['type'] = proj_df.apply(lambda x: x['ivs_project_code'].split("-")[1], axis=1)
proj_df2 = proj_df.copy()
# proj_df2 = proj_df[['type','primary_sector','ivs_project_code']].groupby(by=['type','primary_sector']).count().reset_index()



## Indicator Sectors
    
# st.subheader('Sectors by Indicator')
ind_df = pd.read_excel('./ITTSectors.xlsx')
ind_df.dropna(inplace=True)
ind_df.rename(columns={'indicatorsectorfrom_irt': 'sector'}, inplace=True)
ind_df['type'] = ind_df.apply(lambda x: str(x['ivs_project_code']).split("-")[1], axis=1)


##compare project and Indicator %

st.subheader('Compare Project and Indicators')
st.write('In this section, we compare the proportion of indicators assigned to each sector and the proportion of projects assigned to those sectors.')


if selected_type != 'All':
    filt_ind = ind_df[ind_df['type'] == selected_type]
else:
    filt_ind = ind_df
filt_ind = filt_ind[['sector','ivs_project_code']].groupby(by=['sector']).count().reset_index()


filt_ind['perc'] = filt_ind['ivs_project_code']/filt_ind['ivs_project_code'].sum()
filt_ind['category'] = 'Indicator'

if selected_type != 'All':
    filt_proj = proj_df2[proj_df2['type'] == selected_type]
else:
    filt_proj = proj_df2
filt_proj = filt_proj[['primary_sector','ivs_project_code']].groupby(by=['primary_sector']).count().reset_index()

filt_proj['perc'] = filt_proj['ivs_project_code']/filt_proj['ivs_project_code'].sum()
filt_proj['category'] = 'project'
filt_proj.rename(columns={'primary_sector':'sector'}, inplace=True)

# merge_df = pd.concat([filt_ind, filt_proj])
merge_df = filt_ind.merge(filt_proj, how='outer', on='sector')
merge_df = merge_df[['sector','perc_x','perc_y']]
merge_df.rename(columns={'perc_x':'indicator_perc','perc_y':'project_perc'}, inplace=True)
# merge_df.drop_duplicates(inplace=True)

## combine these 2 into 1 chart


# species = ("Adelie", "Chinstrap", "Gentoo")
sector = merge_df['sector']
sector_means = {
    'Indicators': merge_df['indicator_perc'], #(18.35, 18.43, 14.98),
    'Projects': merge_df['project_perc'],#(38.79, 48.83, 47.50),
}

x = np.arange(len(sector))  # the label locations
width = 0.35  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in sector_means.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute, zorder=2)
    # ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("% of Total")
ax.set_title('Category')
ax.set_xticks(x + width, sector)
# fig.xticks(rotation=90)
plt.xticks(rotation=45, ha='right')
ax.legend(loc='upper left', ncols=3)
plt.grid(axis='y', zorder=1)

# ax.set_ylim(0, 0.5)

col1, col2 = st.columns(2)
with col1:
    st.write(merge_df)
    st.download_button(
        label="Download data as CSV",
        data=convert_df(merge_df),
        file_name= f'IVS-10238-sectors-{selected_type}.csv',
        mime='text/csv'
    )
with col2:
    # st.write(fig)
    st.pyplot(fig)

# r3col1, r3col2, r3col3 = st.columns(3)
# with r3col1:
#     st.bar_chart(filt_ind, y="ivs_project_code", x="sector", height=500)
# with r3col2:
#     st.bar_chart(filt_proj, y="ivs_project_code", x="sector", height=500)



#Sankey Diagram
st.subheader('Sankey Diagram')
st.write('Comparing the projects calculated primary sector to the final display sector')

# st.write(proj_df)

##
def write_sankey(origin_column, destination_column, origin_suffix):
    sector_lut = proj_df['primary_sector'].unique()
    # st.write(sector_lut)
    start_sector_lut = [item for item in sector_lut + origin_suffix]
    full_sector_lut = np.append(sector_lut, start_sector_lut)
    # st.write(sector_lut.index('Health'))
    ## sankey_df
    if selected_type != 'All':
        filter_proj_df = proj_df[proj_df['type'] == selected_type]
    else:
        filter_proj_df = proj_df
    filter_proj_df = filter_proj_df[[origin_column,destination_column,'ivs_project_code']]
    sankey_df = filter_proj_df.groupby(by=[origin_column,destination_column]).count().reset_index()
    sankey_df.rename(columns={'ivs_project_code':'count'}, inplace=True)
    def get_index(x, column):
        if column == origin_column:
            try:
                return int(np.where(full_sector_lut == x[column]+origin_suffix)[0])
            except:
                return None
        else:
            try:
                return int(np.where(full_sector_lut == x[column])[0])
            except:
                return None

        
    sankey_df['origin_ind'] = sankey_df.apply(lambda x: get_index(x, origin_column), axis=1)
    sankey_df['destination_ind'] = sankey_df.apply(lambda x: get_index(x, destination_column), axis=1)
    def get_destination_color(x):
        dest = x['destination_ind']
        color_lut = {
            0:'#9054a1',
            1:'#cc6600',
            2:'#0099cc',
            3:'#3da46a',
            4:'#006661'
        }
        try:
            return color_lut[dest]
        except:
            return '#808080'
    
    sankey_df['color'] = sankey_df.apply(lambda x: get_destination_color(x), axis=1)


    r2col1, r2col2 = st.columns([3,5])

    with r2col1:
        st.write(sankey_df.drop(columns=['origin_ind','destination_ind','color']))
        st.download_button(
            label="Download data as CSV",
            data=convert_df(sankey_df),
            file_name= f'IVS-10238-sankey-{selected_type}-{origin_column}-{destination_column}.csv',
            mime='text/csv'
        )


    with r2col2: 
        fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "black", width = 1.5),
            #   label = ["A1", "A2", "B1", "B2", "C1", "C2"],
            label = full_sector_lut,
            color = "rgba(0,0,0,0)"
            ),
            link = dict(
            source = sankey_df['origin_ind'],
            target = sankey_df['destination_ind'],
            value = sankey_df['count'],
            color = sankey_df['color'],
        ))])

        fig.update_layout(title_text="Sector Adjustments", font_size=18)

        st.plotly_chart(fig, height=800)

write_sankey("primary_sector","display_sector", "_primary")

## Compare DPMS and Final
st.divider()

st.subheader('Comparing DPMS project sectors to display Sector')
st.write('When projects are originally entered into DPMS, project managers assign them to a sector (or sometimes multiple). This diagram compares the sector in DPMs to what we have calculated in display_sector')
write_sankey("dpms_sector","display_sector", "_dpms")

st.header('Appendix: Code logic to calculate Display_sector')
st.write('''PseudoCode:
         1. Pull the projects sector ranks. If rank #1 is one of the big 5 sectors, assign display_sector to that. If not, move to the next step.
         2. If the rank #2 sector is one of the big 5, assign that sector to the project. If not, move onto the next step/
         3. If the rank #1 sector is any of the following, assign it to CPP. Otherwise, go onto the next step:
            -Faith and Development
            -Socaial Accountability and Advocacy
            -GESI
            -Peacebuidling
         4. If rank #1 sector is any of the following, assign to livelihoods:
            -Sustainability
            -Climate Change
         5. If none of the above criteria are met, assign the sector to "Unknown". ''')
st.code('''
    def get_display_sector(x):
    prim_sector = x['primary_sector'] #Rank 1 in counting indicators assigned to each sector
    sec_sector = x['secondary_sector'] # Rank 2 in counting indicators assigned to each sector
    big5 = ['Livelihoods', 'Child Protection and Participation', 'Health','Education', 'Water, Sanitation and Hygiene']
    
    ## if one of the big 5, leave as is
    if prim_sector in big5:
        return prim_sector
    ## next check if secondary sector is one of the big 5. If so, use that.
    elif sec_sector in big5:
        return sec_sector
    ## if a minor sector, assign to one of the big 5.
    elif prim_sector in ['Faith and Development', 
                    'Social Accountability | Advocacy', 
                    'Gender Equality and Social Inclusion', 
                    'Peacebuilding']:
        return 'Child Protection and Participation'
    
    elif prim_sector in ['Climate Change',
                    'Sustainability']:
        return 'Livelihoods'
    
    else:
        return 'Unknown'

    
        #This line runs the above function on each line of the dataframe and assigns it to a new column
df3['display_sector'] = df3.apply(lambda x: get_display_sector(x), axis=1)
'''
)