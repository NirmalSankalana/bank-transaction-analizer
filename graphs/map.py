import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import numpy as np

ARROW_COLOR = "#0077b6"
SENDER_COLOR = "red"
RECEIVER_COLOR = "#70e000"


@st.cache_data
def get_coordinates(branch):
    coordinates = branch.split(', ')
    coordinates = [float(x) for x in coordinates]
    return coordinates


def add_arrow_trace(lat, lon, weight, sender, receiver):
    log_weight = np.log1p(weight / 1000)

    # Calculate the direction vector
    A = np.array([lon[0], lat[0]])
    B = np.array([lon[1], lat[1]])
    v = B - A
    w = v / np.linalg.norm(v)  # Normalize the vector
    u = np.array([-v[1], v[0]])  # Perpendicular vector

    # Arrowhead parameters
    arrow_length = log_weight * 0.2
    arrow_width = arrow_length * 0.05

    # Calculate arrowhead points
    P = B - arrow_length * w
    S = P - arrow_width * u
    T = P + arrow_width * u

    return [
        go.Scattermapbox(
            lat=lat,
            lon=lon,
            mode='lines',
            line=dict(width=log_weight, color=ARROW_COLOR),
            text=[f'{sender} -> {receiver}: ${weight}'],
            hoverinfo='text'
        ),
        go.Scattermapbox(
            lon=[S[0], T[0], B[0], S[0]],
            lat=[S[1], T[1], B[1], S[1]],
            mode='lines',
            fill='toself',
            fillcolor=ARROW_COLOR,
            line_color=ARROW_COLOR,
            hoverinfo='skip'
        )
    ]


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
        marker=dict(size=10, color=SENDER_COLOR),
        text=[node for node in sender_branches],
        textposition="top center"
    )

    receiver_trace = go.Scattermapbox(
        lat=[pos[node][0] for node in receiver_branches],
        lon=[pos[node][1] for node in receiver_branches],
        mode='markers+text',
        marker=dict(size=10, color=RECEIVER_COLOR),
        text=[node for node in receiver_branches],
        textposition="top center"
    )

    for u, v, data in G.edges(data=True):
        lat = [pos[u][0], pos[v][0]]
        lon = [pos[u][1], pos[v][1]]
        weight = data['weight']
        edge_trace.extend(add_arrow_trace(lat, lon, weight, u, v))

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
