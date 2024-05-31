import streamlit as st
from pyvis.network import Network
import networkx as nx


@st.cache_resource
def ego(filtered_df):
    G = nx.Graph()
    G.add_nodes_from(filtered_df['Sender Name'])
    G.add_nodes_from(filtered_df['Receiver Name'])
    edges = [(row['Sender Name'], row['Receiver Name'])
             for idx, row in filtered_df.iterrows()]
    G.add_edges_from(edges)

    # Create a PyVis network
    g = Network(height='450px', width='100%')
    g.from_nx(G)
    return g
