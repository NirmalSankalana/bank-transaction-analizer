import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import numpy as np


@st.cache_data
def get_coordinates(branch):
    coordinates = branch.split(', ')
    coordinates = [float(x) for x in coordinates]
    return coordinates


def transaction_map(filtered_df):
    st.subheader('Interactive Map of Transactions')
    G = nx.DiGraph()

    sender_branches = set()
    receiver_branches = set()

    for idx, row in filtered_df.iterrows():
        sender_coords = get_coordinates(row['Sender Account Branch'])
        receiver_coords = get_coordinates(row['Receiver Account Branch'])
        sender_branch = row['Sender Account Branch']
        receiver_branch = row['Receiver Account Branch']
        sender = row['Sender Name']
        receiver = row['Receiver Name']

        sender_branches.add(sender)
        receiver_branches.add(receiver)

        if sender not in G:
            G.add_node(sender, pos=sender_coords)
        if receiver not in G:
            G.add_node(receiver, pos=receiver_coords)

        G.add_edge(sender, receiver, weight=row['Amount'])

    pos = nx.get_node_attributes(G, 'pos')
    edge_trace = []

    sender_trace = go.Scattermapbox(
        lat=[pos[node][0] for node in sender_branches],
        lon=[pos[node][1] for node in sender_branches],
        mode='markers+text',
        marker=dict(size=10, color='blue'),
        text=[node for node in sender_branches],
        textposition="top center"
    )

    receiver_trace = go.Scattermapbox(
        lat=[pos[node][0] for node in receiver_branches],
        lon=[pos[node][1] for node in receiver_branches],
        mode='markers+text',
        marker=dict(size=10, color='green'),
        text=[node for node in receiver_branches],
        textposition="top center"
    )

    for u, v, data in G.edges(data=True):
        lat = [pos[u][0], pos[v][0], None]
        lon = [pos[u][1], pos[v][1], None]
        weight = data['weight']
        log_weight = np.log1p(weight / 1000)
        edge_trace.append(go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='lines',
            line=dict(width=log_weight, color='#1EC677'),
            text=[f'{u} -> {v}: ${data["weight"]}'],
            hoverinfo='text'
        ))

    fig = go.Figure(data=edge_trace + [sender_trace, receiver_trace])
    fig.update_layout(
        mapbox=dict(
            # Replace with your actual Mapbox access token
            accesstoken='your_mapbox_access_token',
            style="carto-positron",
            zoom=3,
            center=dict(lat=39, lon=-95)
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)
