import streamlit as st
import plotly.graph_objects as go
import pandas as pd


@st.cache_resource
def generate_sankey(df):
    # Combine sender and receiver names
    all_nodes = list(df['Sender Name'].unique()) + \
        list(df['Receiver Name'].unique())
    node_labels = list(set(all_nodes))

    # Define the links
    links = []
    for _, row in df.iterrows():
        source = node_labels.index(row['Sender Name'])
        target = node_labels.index(row['Receiver Name'])
        value = row['Amount']
        links.append({'source': source, 'target': target, 'value': value})

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
        ),
        link=dict(
            source=[link['source'] for link in links],
            target=[link['target'] for link in links],
            value=[link['value'] for link in links],
        ))])

    fig.update_layout(title_text="Cash Flow Diagram", font_size=12)
    return fig
