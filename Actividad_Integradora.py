import pandas as pd
import streamlit as st
import plotly.express as px
import statistics

st.set_page_config(page_title="Organized Crime", page_icon="😵‍💫", layout="wide")

@st.cache
def get_data_from_csv():
    df = pd.read_excel('Police_Department_Incident_Reports__2018_to_Present.xlsx')
    df = df.replace({"": "None"})
    df = df.rename(columns={'Incident Year': 'Incident_Year', 'Incident Day of Week': 'Incident_Day_of_Week', 'Analysis Neighborhood': 'Analysis_Neighborhood', 'Incident ID': 'Incident_ID', 'Incident Subcategory': 'Incident_SubCategory', 'Incident Time': 'Incident_Time','Incident Number': 'Incident_Numbers'})
    #st.dataframe(df)

    # Add "hour" column to dataframe.

    #df["Hour"] = pd.to_datetime(df["Incident_Time"], format="%H:%M").dt.hour
    return df
df = get_data_from_csv()

#--SideBar--

st.sidebar.header("Please Filter Here:")
year = st.sidebar.multiselect(
    "Select the Year:",
    options=df["Incident_Year"].unique(),
    default=df["Incident_Year"].unique()
)

day_week = st.sidebar.multiselect(
    "Select the Day of Week:",
    options=df["Incident_Day_of_Week"].unique(),
    default=df["Incident_Day_of_Week"].unique()
)

neighborhood = st.sidebar.multiselect(
    "Select the Neighborhood:",
    options=df["Analysis_Neighborhood"].unique(),
    default=df["Analysis_Neighborhood"].unique()
)

df_selection = df.query(
    "Incident_Year == @year & Incident_Day_of_Week == @day_week & Analysis_Neighborhood == @neighborhood"
)

#st.dataframe(df_selection)

# ----- MAINPAGE -----
st.title(":bar_chart: Crime Dashboard")
st.markdown("##")

# TOP KPI's

incidents = int(df_selection["Incident_ID"].count())
incident_day = statistics.mode(df_selection['Incident_Day_of_Week'])
#incident_time = statistics.mode(df_selection['Incident_Time'])

left_column, right_column = st.columns(2)
with left_column:
    st.subheader("Total Incidents")
    st.subheader(f"{incidents:,}")
with right_column:
    st.subheader("Day with most probability of Incidents")
    st.subheader(incident_day)
#with right_column:
    #st.subheader("Most Incident Time")
    #st.subheader(incident_time)

st.markdown("---")



# Number Incidents by Incident Category.

incidents_by_incident_category = (
    df_selection.groupby(by=["Incident_SubCategory"]).count()[["Incident_Numbers"]].sort_values(by="Incident_Numbers")
)

fig_incidents_by_category = px.bar(
    incidents_by_incident_category,
    x = "Incident_Numbers",
    y = incidents_by_incident_category.index,
    orientation="h",
    title = "<b>Total Incidents by SubCategories<b>",
    color_discrete_sequence=["#008388"] * len(incidents_by_incident_category),
    template="plotly_white",
)
fig_incidents_by_category.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)



# Incident by Hour [Bar Chart]

# --- Hide Streamlit Style ---

hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """

st.markdown(hide_st_style, unsafe_allow_html=True)

# Combinar las columnas de incidentes en una sola columna
df['Incidente'] = df[['Incident Category', 'Incident Date', 'Number of Incidents']].astype(str).apply(lambda x: ', '.join(x.dropna()), axis=1)

# Configurar la clave de acceso de Mapbox
px.set_mapbox_access_token('pk.eyJ1IjoiZW5yaXF1ZW1vbnNpMTkiLCJhIjoiY2xpeHkwdGRvMGFtMTNlbzgxNzE3MjZ5dSJ9.63FyiBhM_U3Gu5B78rbmWg')


# Crear el gráfico interactivo
fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', hover_name='Incidente', hover_data=['Incidente'],
                        zoom=10, height=500)

fig.update_layout(mapbox_style="mapbox://styles/mapbox/satellite-v9")
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_incidents_by_category, use_container_width=True)
#middle_column.plotly_chart(fig_incidents_by_category, use_container_width=True)
right_column.plotly_chart(fig, use_container_width=True)
