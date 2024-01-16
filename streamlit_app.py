import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
st.set_page_config(layout="wide")


st.header('Finding Project Sectors FY23')
st.header('WVC-10238')

with st.expander('About this app'):
    st.write('This app has been created using streamlit to visualize our data. The source code can be found at      "Shared - IVS/3. Management/Data Quality Control/Data Cleaning/FY23 Cleaning/Project Sectors/WVC-10238-Project-Sectors-FY23"')
    st.write('Written by Timmy Bender - last updated Jan 16, 2024')


## sidebar

type_options = ['GNT', 'PNS','GIK','SPN','WFP','OTH']
selected_type = st.sidebar.selectbox("Choose a Project Type to get started", options=type_options)

## Project SEctors

proj_df = pd.read_excel('./ProjectSectors.xlsx')
proj_df['type'] = proj_df.apply(lambda x: x['ivs_project_code'].split("-")[1], axis=1)
proj_df2 = proj_df[['type','primary_sector','ivs_project_code']].groupby(by=['type','primary_sector']).count().reset_index()


r1col1, r1col2 = st.columns(2)
with r1col1:
    st.dataframe(proj_df2)

with r1col2:
    st.bar_chart(proj_df2, x="type", y="ivs_project_code", color="primary_sector", height=500)



## Indicator Sectors
    
st.subheader('Sectors by Indicator')
ind_df = pd.read_excel('./ITTSectors.xlsx')
ind_df.dropna(inplace=True)
ind_df.rename(columns={'indicatorsectorfrom_irt': 'sector'}, inplace=True)
ind_df['type'] = ind_df.apply(lambda x: str(x['ivs_project_code']).split("-")[1], axis=1)

count_ind = ind_df[['type','sector','ivs_project_code']].groupby(by=['type','sector']).count().reset_index()

r2col1, r2col2 = st.columns(2)
with r2col1:
    st.dataframe(count_ind)

with r2col2:
    st.bar_chart(count_ind, x="type", y=["ivs_project_code"], color="sector", height=500)

##compare project and Indicator %

st.subheader('Compare Project and Indicators')

filt_ind = count_ind[count_ind['type'] == selected_type]
filt_ind['perc'] = filt_ind['ivs_project_code']/filt_ind['ivs_project_code'].sum()
filt_ind['category'] = 'Indicator'


filt_proj = proj_df2[proj_df2['type'] == selected_type]
filt_proj['perc'] = filt_proj['ivs_project_code']/filt_proj['ivs_project_code'].sum()
filt_proj['category'] = 'project'
filt_proj.rename(columns={'primary_sector':'sector'}, inplace=True)

merge_df = pd.concat([filt_ind, filt_proj])
st.write(merge_df)

## combine these 2 into 1 chart

st.bar_chart(merge_df, x="sector", y="perc", color="category")

species = ("Adelie", "Chinstrap", "Gentoo")
penguin_means = {
    'Bill Depth': (18.35, 18.43, 14.98),
    'Bill Length': (38.79, 48.83, 47.50),
    'Flipper Length': (189.95, 195.82, 217.19),
}

x = np.arange(len(species))  # the label locations
width = 0.25  # the width of the bars
multiplier = 0

fig, ax = plt.subplots(layout='constrained')

for attribute, measurement in penguin_means.items():
    offset = width * multiplier
    rects = ax.bar(x + offset, measurement, width, label=attribute)
    ax.bar_label(rects, padding=3)
    multiplier += 1

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Length (mm)')
ax.set_title('Penguin attributes by species')
ax.set_xticks(x + width, species)
ax.legend(loc='upper left', ncols=3)
ax.set_ylim(0, 250)

st.write(fig)

# r3col1, r3col2, r3col3 = st.columns(3)
# with r3col1:
#     st.bar_chart(filt_ind, y="ivs_project_code", x="sector", height=500)
# with r3col2:
#     st.bar_chart(filt_proj, y="ivs_project_code", x="sector", height=500)

#Sankey Diagram


fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = ["A1", "A2", "B1", "B2", "C1", "C2"],
      color = "blue"
    ),
    link = dict(
      source = [0, 1, 0, 2, 3, 3], # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = [2, 3, 3, 4, 4, 5],
      value = [8, 4, 2, 8, 4, 2]
  ))])

# fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
st.plotly_chart(fig)