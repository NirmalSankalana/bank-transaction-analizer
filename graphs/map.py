import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import numpy as np


@st.cache_data
def get_coordinates(branch):
    coordinates = branch.split(', ')
    coordinates = [float(x) for x in coordinates]
    return coordinates


def add_arrow_trace(lat, lon, weight, sender, receiver):
    log_weight = np.log1p(weight / 1000)
    arrow_size = log_weight / 5

    # Calculate direction vector
    direction = np.array([lat[1] - lat[0], lon[1] - lon[0]])
    norm = np.linalg.norm(direction)
    if norm == 0:  # Prevent division by zero
        norm = 1
    direction = direction / norm

    # Calculate arrowhead position
    arrowhead_lat = lat[1] - direction[0] * arrow_size * 0.5
    arrowhead_lon = lon[1] - direction[1] * arrow_size * 0.5

    return go.Scattermapbox(
        lat=[lat[0], lat[1], arrowhead_lat],
        lon=[lon[0], lon[1], arrowhead_lon],
        mode='lines+markers',
        line=dict(width=log_weight, color='#1EC677'),
        marker=dict(size=[0, 0, arrow_size], color='#1EC677',
                    symbol=['circle', 'circle', 'triangle']),
        text=[f'{sender} -> {receiver}: ${weight}'],
        hoverinfo='text'
    )


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
        marker=dict(size=10, color='red'),
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
        lat = [pos[u][0], pos[v][0]]
        lon = [pos[u][1], pos[v][1]]
        weight = data['weight']
        edge_trace.append(add_arrow_trace(lat, lon, weight, u, v))

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
