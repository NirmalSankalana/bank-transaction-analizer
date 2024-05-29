import streamlit as st
import plotly.express as px


@st.cache_resource
def generate_pie_chart(df, column, title):
    fig = px.pie(df, names=column, title=title)
    return fig
