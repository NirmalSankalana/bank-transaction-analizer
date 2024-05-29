import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import altair as alt
import folium
import networkx as nx
from streamlit_folium import st_folium
import streamlit.components.v1 as components
import numpy as np
import plotly.graph_objects as go

from graphs.timeline import display_transactions
from graphs.sankey import generate_sankey
from graphs.pie import generate_pie_chart
from graphs.ego import ego
metric_style = """
    <style>
        .metric-box {
            background-color: #f0f2f6;
            border-radius: 6px;
            padding: 16px;
            text-align: center;
            margin: 8px 0;
        }
        .metric-title {
            font-size: 16px;
            color: #333;
        }
        .metric-value {
            font-size: 32px;
            color: #1f77b4;
        }
    </style>
"""
# token = "pk.eyJ1IjoibmlybWFsc2Fua2FsYW5hIiwiYSI6ImNsd3MybnkwYTAydmcyam9leGVhYWplZ24ifQ.0zwIa3vIFnu2yx79hPCbCA"
# Page configuration
st.set_page_config(
    page_title="Bank Transactions Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")
# Display metrics with styling
st.markdown(metric_style, unsafe_allow_html=True)
# Load the data
df = pd.read_csv('data/bank-transactions.csv')

with st.sidebar:
    st.title('Bank Transactions Dashboard')
    names = st.multiselect('Select a name', df['Sender Name'].unique())
    phone_numbers = st.multiselect(
        'Select a phone number', df['Sender Phone Number'].unique())
    acc_no = st.multiselect('Select an account number',
                            df['Sender Account'].unique())

filtered_df = df.copy()

# Apply filters conditionally
if names:
    filtered_df = filtered_df[filtered_df['Sender Name'].isin(
        names) | filtered_df['Receiver Name'].isin(names)]
if phone_numbers:
    filtered_df = filtered_df[filtered_df['Sender Phone Number'].isin(
        phone_numbers) | filtered_df['Receiver Phone Number'].isin(
            phone_numbers)]
if acc_no:
    filtered_df = filtered_df[filtered_df['Sender Account'].isin(acc_no) | filtered_df['Receiver Account'].isin(
        acc_no)]

G = ego(filtered_df)

# Save the network to an HTML file
html_file_path = 'network_graph.html'
G.write_html(html_file_path)


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


if names or phone_numbers or acc_no:
    colk1, colk2, colk3 = st.columns((2.7, 2.7, 2.7), gap='medium')
    with colk1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Total Transactions</div>
                <div class="metric-value">{filtered_df.shape[0]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colk2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Total Amount</div>
                <div class="metric-value">{filtered_df['Amount'].sum()} USD</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colk3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Other KPI</div>
                <div class="metric-value">123456</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    colp1, colp2, colp3, colp4 = st.columns((2, 2, 2, 2), gap='small')
    with colp1:
        transaction_purpose_pie = generate_pie_chart(
            filtered_df, 'Purpose of Transaction', 'Transaction Purposes Distribution')
        st.plotly_chart(transaction_purpose_pie, use_container_width=True)
    with colp2:
        transaction_type_pie = generate_pie_chart(
            filtered_df, 'Transaction Type', 'Transaction Types Distribution')
        st.plotly_chart(transaction_type_pie, use_container_width=True)
    with colp3:
        sender_name_pie = generate_pie_chart(
            filtered_df, 'Sender Name', 'Sender Names Distribution')
        st.plotly_chart(sender_name_pie, use_container_width=True)
    with colp4:
        receiver_name_pie = generate_pie_chart(
            filtered_df, 'Receiver Name', 'Receiver Names Distribution')
        st.plotly_chart(receiver_name_pie, use_container_width=True)

    sankey_fig = generate_sankey(filtered_df)

    st.plotly_chart(sankey_fig, use_container_width=True)

    col1, col2 = st.columns((4, 4), gap='small')

    with col1:
        transaction_map(filtered_df)

    with col2:
        # Read the HTML file
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Display the HTML content in Streamlit
        components.html(html_content, height=500, width=700)

    display_transactions(filtered_df)

    summary = filtered_df.groupby('Sender Account').agg(
        sender_name=('Sender Name', 'first'),
        total_sent=('Amount', 'sum'),
        # Assuming 'Amount' column is positive for both sent and received transactions
        total_received=('Amount', 'sum'),
        transactions_received=('ID', 'count'),
        account_type=('Sender Account Type', 'first'),
        branch_involved=('Sender Account Branch',
                         lambda x: ', '.join(x.unique()))
    ).reset_index()

    st.subheader('Summary of Transactions')
    st.dataframe(summary)
    st.subheader('Detailed Transactions List')
    st.dataframe(filtered_df[[
        'ID', 'Sender Account', 'Sender Name', 'Receiver Account', 'Receiver Name', 'Amount', 'Date and Time',
        'Transaction Type', 'Purpose of Transaction'
    ]])

    # related_accounts = filtered_df.groupby('Receiver Account').agg(
    #     total_sent=('Amount', 'sum'),
    #     total_received=('Amount', 'sum')
    # ).reset_index()

    # st.subheader('Related Accounts')
    # st.dataframe(related_accounts)


else:
    colk1, colk2, colk3 = st.columns((2.7, 2.7, 2.7), gap='medium')
    with colk1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Total Transactions</div>
                <div class="metric-value"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colk2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Total Amount</div>
                <div class="metric-value"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with colk3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-title">Other KPI</div>
                <div class="metric-value"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
