import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#######################################
# PAGE SETUP
#######################################

st.set_page_config(
    page_title="Environment Dashboard", page_icon=":bar_chart:", layout="wide"
)
st.markdown(
    "<h1 style='text-align: center;margin-bottom:2%;'>Environment Monitoring Data Visualization</h1>",
    unsafe_allow_html=True,
)

conn = st.connection("gsheets", type=GSheetsConnection)

#######################################
# DATA LOADING
#######################################


@st.cache_data
def load_data():
    data = conn.read(worksheet="DeviceData")
    return data


df = load_data()
with st.expander("Data Preview"):
    st.dataframe(df)


#######################################
# VISUALIZATION METHODS
#######################################


# Plot Monthly Temperature
def line_temp_chart(df):
    result = df.groupby("Month").mean()
    months = df["Month"].unique().tolist()[::-1]
    y1 = result["Temperature (°C)"].tolist()[::-1]
    fig = px.line(
        x=months,
        y=y1,
        labels={"x": "Months", "y": "Temperature (°C)"},
        # color="Scenario",
        markers=True,
        title="Temperature",
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        title_text="Temperature",
        title_font=dict(size=26),
    )
    st.plotly_chart(fig, use_container_width=True)


# Plot Monthly Humidity
def line_humidity_chart(df):
    result = df.groupby("Month").mean()
    months = df["Month"].unique().tolist()[::-1]
    y1 = result["Humidity (%)"].tolist()[::-1]
    fig = px.line(
        x=months,
        y=y1,
        labels={"x": "Months", "y": "Humidity (%)"},
        # color="Scenario",
        markers=True,
    )
    fig.update_traces(
        textposition="top center",
        line=dict(color="red"),
    )
    fig.update_layout(
        title_text="Humidity",
        title_font=dict(size=26),
    )
    st.plotly_chart(fig, use_container_width=True)


# Grouped Bar chart for particulate matter
@st.cache_data
def grouped_bar_chart(df):
    result = df.groupby("Month").mean()
    months = df["Month"].unique().tolist()[::-1]
    y1 = result["PM10 Particulate Matter (µg/m3)"].tolist()[::-1]
    y2 = result["PM2.5 Particulate Matter (µg/m3)"].tolist()[::-1]
    y3 = result["PM1 Particulate Matter (µg/m3)"].tolist()[::-1]
    fig = go.Figure(
        data=[
            go.Bar(name="PM10 Particulate Matter", x=months, y=y1),
            go.Bar(name="PM2.5 Particulate Matter", x=months, y=y2),
            go.Bar(name="PM1 Particulate Matter", x=months, y=y3),
        ]
    )
    # Change the bar mode
    fig.update_layout(
        barmode="group",
        height=400,
        margin=dict(l=25, r=25, t=50, b=20, pad=8),
        title="Monthly Average Particulate Matter Values",
        title_font=dict(size=26),
    )
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def plot_gauge(
    indicator_number,
    indicator_color,
    indicator_suffix,
    indicator_title,
    min_bound,
    max_bound,
):
    fig = go.Figure(
        go.Indicator(
            value=indicator_number,
            mode="gauge+number",
            domain={"x": [0, 1], "y": [0, 1]},
            number={
                "suffix": indicator_suffix,
                "font.size": 26,
            },
            gauge={
                "axis": {"range": [min_bound, max_bound], "tickwidth": 1},
                "bar": {"color": indicator_color},
            },
            title={
                "text": indicator_title,
                "font": {"size": 28},
            },
        )
    )
    fig.update_layout(
        # paper_bgcolor="lightgrey",
        height=300,
        margin=dict(l=15, r=15, t=100, b=10, pad=15),
    )
    st.plotly_chart(fig, use_container_width=True)


#######################################
# Summary and statistics
#######################################


@st.cache_data
def print_stats(selected_parameter):
    st.write(f"Summary Statistics for {selected_parameter}:")
    # st.write(df[selected_parameter].describe())

    # Display additional statistics
    # st.write("Additional Statistics:")
    st.write(f"Mean: {df[selected_parameter].mean()}")
    st.write(f"Median (50th percentile): {df[selected_parameter].median()}")
    st.write(f"Standard Deviation: {df[selected_parameter].std()}")
    st.write(f"Minimum: {df[selected_parameter].min()}")
    st.write(f"Maximum: {df[selected_parameter].max()}")


#######################################
# STREAMLIT LAYOUT
#######################################

top_left_column, top_right_column = st.columns((2, 1))
bottom_left_column, bottom_right_column = st.columns(2)


with top_left_column:
    column_1, column_2, column_3 = st.columns(3)

    with column_1:
        plot_gauge(
            df["Carbon Monoxide CO (ppm)"].mean(),
            "#0068C9",
            " ppm",
            "Carbon Monoxide",
            df["Carbon Monoxide CO (ppm)"].min(),
            df["Carbon Monoxide CO (ppm)"].max(),
        )

    with column_2:
        plot_gauge(
            df["Ozone O3 (ppm)"].mean(),
            "#FF8700",
            " ppm",
            "Ozone",
            df["Ozone O3 (ppm)"].min(),
            df["Ozone O3 (ppm)"].max(),
        )

    with column_3:
        plot_gauge(
            df["Nitrogen Dioxide NO2 (ppm)"].mean(),
            "#29B09D",
            " ppm",
            "Nitrogen Dioxide",
            df["Nitrogen Dioxide NO2 (ppm)"].min(),
            df["Nitrogen Dioxide NO2 (ppm)"].max(),
        )

with top_right_column:
    with st.expander("View Summary"):
        selected_parameter = st.selectbox(
            "Select a parameter",
            [
                "Carbon Monoxide CO (ppm)",
                "Ozone O3 (ppm)",
                "Nitrogen Dioxide NO2 (ppm)",
            ],
        )
        print_stats(selected_parameter)


with bottom_left_column:
    selected_columns = [
        "Temperature (°C)",
        "Month",
    ]
    df_selected = df[selected_columns]
    line_temp_chart(df_selected)

with bottom_right_column:
    selected_columns = [
        "Humidity (%)",
        "Month",
    ]
    df_selected = df[selected_columns]
    line_humidity_chart(df_selected)


selected_columns = [
    "PM10 Particulate Matter (µg/m3)",
    "PM2.5 Particulate Matter (µg/m3)",
    "PM1 Particulate Matter (µg/m3)",
    "Month",
]
df_selected = df[selected_columns]
grouped_bar_chart(df_selected)
