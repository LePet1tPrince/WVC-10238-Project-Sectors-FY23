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

with st.sidebar.expander('About this app'):
    st.write('This app has been created using streamlit to visualize our data. The source code can be found at      "Shared - IVS/3. Management/Data Quality Control/Data Cleaning/FY23 Cleaning/Project Sectors/WVC-10238-Project-Sectors-FY23"')
    st.write('Written by Timmy Bender - last updated Jan 17, 2024')


## sidebar

type_options = ['GNT', 'PNS','GIK','SPN','WFP','OTH', 'All']
selected_type = st.sidebar.selectbox("Choose a Project Type to get started", options=type_options)

## Project Sectors

proj_df = pd.read_excel('./ProjectSectors.xlsx')
proj_df['type'] = proj_df.apply(lambda x: x['ivs_project_code'].split("-")[1], axis=1)
proj_df2 = proj_df.copy()
# proj_df2 = proj_df[['type','primary_sector','ivs_project_code']].groupby(by=['type','primary_sector']).count().reset_index()


# r1col1, r1col2 = st.columns(2)
# with r1col1:
#     st.dataframe(proj_df2)

# with r1col2:
#     st.bar_chart(proj_df2, x="type", y="ivs_project_code", color="primary_sector", height=500)



## Indicator Sectors
    
# st.subheader('Sectors by Indicator')
ind_df = pd.read_excel('./ITTSectors.xlsx')
ind_df.dropna(inplace=True)
ind_df.rename(columns={'indicatorsectorfrom_irt': 'sector'}, inplace=True)
ind_df['type'] = ind_df.apply(lambda x: str(x['ivs_project_code']).split("-")[1], axis=1)

# count_ind = ind_df[['type','sector','ivs_project_code']].groupby(by=['type','sector']).count().reset_index()

# r2col1, r2col2 = st.columns(2)
# with r2col1:
#     st.dataframe(count_ind)

# with r2col2:
#     st.bar_chart(count_ind, x="type", y=["ivs_project_code"], color="sector", height=500)

##compare project and Indicator %

st.subheader('Compare Project and Indicators')
st.write('Comparing the proportion of indicators assigned to each sector to the proportion for projects assigned to those sectors.')

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
sector_lut = proj_df['primary_sector'].unique()
start_sector_lut = [item for item in sector_lut + '_primary']
full_sector_lut = np.append(sector_lut, start_sector_lut)
# st.write(sector_lut.index('Health'))
## sankey_df
if selected_type != 'All':
    filter_proj_df = proj_df[proj_df['type'] == selected_type]
else:
    filter_proj_df = proj_df

filter_proj_df = filter_proj_df[['primary_sector','display_sector','ivs_project_code']]
sankey_df = filter_proj_df.groupby(by=['primary_sector','display_sector']).count().reset_index()
sankey_df.rename(columns={'ivs_project_code':'count'}, inplace=True)
def get_index(x, column):
    if column == 'primary_sector':
        try:
            return int(np.where(full_sector_lut == x[column]+'_primary')[0])
        except:
            return None
    else:
        try:
            return int(np.where(full_sector_lut == x[column])[0])
        except:
            return None

    
sankey_df['primary_ind'] = sankey_df.apply(lambda x: get_index(x, 'primary_sector'), axis=1)
sankey_df['display_ind'] = sankey_df.apply(lambda x: get_index(x, 'display_sector'), axis=1)

r2col1, r2col2 = st.columns(2)

with r2col1:
    st.write(sankey_df)
    st.download_button(
        label="Download data as CSV",
        data=convert_df(sankey_df),
        file_name= f'IVS-10238-sankey-{selected_type}.csv',
        mime='text/csv'
    )


with r2col2: 
    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 50,
        thickness = 20,
        line = dict(color = "black", width = 1.5),
        #   label = ["A1", "A2", "B1", "B2", "C1", "C2"],
        label = full_sector_lut,
        color = "blue"
        ),
        link = dict(
        source = sankey_df['primary_ind'],#[0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
        target = sankey_df['display_ind'],#[2, 3, 3, 4, 4, 5],
        value = sankey_df['count'],#[8, 4, 2, 8, 4, 2]
    ))])

    fig.update_layout(title_text="Sector Adjustments", font_size=20)

    st.plotly_chart(fig, height=800)

# buffer to use for excel writer
# buffer = io.BytesIO()
# with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
#     # Write each dataframe to a different worksheet.
#     sankey_df.to_excel(writer, sheet_name='Sheet1', index=False)

#     # writer.save()

#     download2 = st.download_button(
#         label="Download data as Excel",
#         data=buffer,
#         file_name= f'IVS-10238-download-{selected_type}.xlsx',
#         mime="application/vnd.ms-excel"
    # )