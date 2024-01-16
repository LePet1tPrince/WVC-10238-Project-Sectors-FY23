import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(layout="wide")


st.header('Finding Project Sectors FY23')
st.header('WVC-10238')

with st.expander('About this app'):
    st.write('This app has been created using streamlit to visualize our data. The source code can be found at      "Shared - IVS/3. Management/Data Quality Control/Data Cleaning/FY23 Cleaning/Project Sectors/WVC-10238-Project-Sectors-FY23"')
    st.write('Written by Timmy Bender - last updated Jan 16, 2024')


proj_df = pd.read_excel('../ProjectSectors.xlsx')
proj_df['type'] = proj_df.apply(lambda x: x['ivs_project_code'].split("-")[1], axis=1)
proj_df2 = proj_df.groupby(by=['type','sector']).count().reset_index()

col1, col2 = st.columns(2)
with col1:
    st.dataframe(proj_df2)
# labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# sizes = [15, 30, 45, 10]

# fig, ax = plt.subplots()
# ax.pie(sizes, labels=labels)

# st.write(fig)
with col2:
    st.bar_chart(proj_df2, x="type", y="ivs_project_code", color="sector", height=500)