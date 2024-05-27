import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
import folium
import networkx as nx
from streamlit_folium import st_folium
import numpy as np

metric_style = """
    <style>
        .metric-box {
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 10px;
            text-align: center;
            margin: 10px 0;
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

# Page configuration
st.set_page_config(
    page_title="Bank Transactions Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

# Load the data
df = pd.read_csv('data/bank-transactions.csv')

#######################
# Sidebar
with st.sidebar:
    st.title('Bank Transactions Dashboard')
    names = st.multiselect('Select a name', df['Sender Name'].unique())
    phone_numbers = st.multiselect(
        'Select a phone number', df['Sender Phone Number'].unique())
    acc_no = st.multiselect('Select an account number',
                            df['Sender Account'].unique())

# Start with the full DataFrame
filtered_df = df.copy()

# Apply filters conditionally
if names:
    filtered_df = filtered_df[filtered_df['Sender Name'].isin(names)]
if phone_numbers:
    filtered_df = filtered_df[filtered_df['Sender Phone Number'].isin(
        phone_numbers)]
if acc_no:
    filtered_df = filtered_df[filtered_df['Sender Account'].isin(acc_no)]


def get_coordinates(branch):
    coordinates = branch.split(', ')
    coordinates = [eval(x) for x in coordinates]
    return coordinates


def transaction_map(filtered_df):
    st.subheader('Interactive Map of Transactions')
    m = folium.Map(location=[39, -95], zoom_start=4)
    G = nx.DiGraph()

    sender_branches = set()
    receiver_branches = set()

    for idx, row in filtered_df.iterrows():
        sender_coords = get_coordinates(row['Sender Account Branch'])
        receiver_coords = get_coordinates(row['Receiver Account Branch'])
        sender = row['Sender Account Branch']
        receiver = row['Receiver Account Branch']

        sender_branches.add(sender)
        receiver_branches.add(receiver)

        if sender not in G:
            G.add_node(sender, pos=sender_coords)
        if receiver not in G:
            G.add_node(receiver, pos=receiver_coords)

        G.add_edge(sender, receiver, weight=row['Amount'])

    pos = nx.get_node_attributes(G, 'pos')
    for node, (lat, lon) in pos.items():
        if node in sender_branches and node in receiver_branches:
            color = 'orange'  # Node is both sender and receiver
        elif node in sender_branches:
            color = 'blue'  # Node is only sender
        elif node in receiver_branches:
            color = 'green'  # Node is only receiver
        else:
            color = 'red'  # Fallback color if the logic fails

        folium.Marker(
            location=[lat, lon],
            popup=node,
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Draw edges on the map
    for u, v, data in G.edges(data=True):
        weight = data['weight']
        # Apply log scale (log1p for log(1 + x) to avoid log(0))
        log_weight = np.log1p(weight/100)
        folium.PolyLine(
            [pos[u], pos[v]],
            weight=log_weight,  # Use log_weight for thickness
            color='#1EC677'
        ).add_to(m)

    st_folium(m, width=700, height=500)


def display_transactions(filtered_df):
    st.subheader('Transaction Timeline')
    filtered_df['Date and Time'] = pd.to_datetime(filtered_df['Date and Time'])
    transaction_timeseries = filtered_df.groupby([pd.Grouper(
        key='Date and Time', freq='D'), 'Transaction Type'])['Amount'].sum().reset_index()
    transaction_timeseries = transaction_timeseries.pivot(
        index='Date and Time', columns='Transaction Type', values='Amount').reset_index()
    transaction_timeseries = transaction_timeseries.melt(
        'Date and Time', var_name='Transaction Type', value_name='Amount')

    timeline = alt.Chart(transaction_timeseries).mark_bar().encode(
        x=alt.X('Date and Time:T', title='Date'),
        y=alt.Y('Amount:Q', title='Transaction Amount'),
        color='Transaction Type:N'
    ).interactive()
    st.altair_chart(timeline, use_container_width=True)


# Display metrics with styling
st.markdown(metric_style, unsafe_allow_html=True)


def generate_pie_chart(df, column, title):
    fig = px.pie(df, names=column, title=title)
    return fig


def generate_sankey(df):
    # Define the nodes
    all_nodes = list(df['Sender Account'].unique()) + \
        list(df['Receiver Account'].unique())
    node_labels = list(set(all_nodes))

    # Define the links
    links = []
    for _, row in df.iterrows():
        source = node_labels.index(row['Sender Account'])
        target = node_labels.index(row['Receiver Account'])
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


if names or phone_numbers or acc_no:
    colk1, colk2, colk3 = st.columns((2.7, 2.7, 2.7), gap='small')
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

    # Generate the Sankey diagram
    sankey_fig = generate_sankey(filtered_df)

    st.plotly_chart(sankey_fig, use_container_width=True)

    col1, col2 = st.columns((4, 4), gap='small')

    with col1:
        transaction_map(filtered_df)

    with col2:
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

    col3, col4 = st.columns((5.5, 2.5), gap='small')

    with col3:
        st.subheader('Detailed Transactions List')
        st.dataframe(filtered_df[[
            'ID', 'Sender Account', 'Receiver Account', 'Amount', 'Date and Time',
            'Transaction Type', 'Purpose of Transaction'
        ]])

    with col4:
        related_accounts = filtered_df.groupby('Receiver Account').agg(
            total_sent=('Amount', 'sum'),
            total_received=('Amount', 'sum')
        ).reset_index()

        st.subheader('Related Accounts')
        st.dataframe(related_accounts)

    display_transactions(filtered_df)
else:
    st.subheader(
        'No transactions selected. Please select filters from the sidebar to display data.')
    # Display empty map and tables
    m = folium.Map(location=[39, -95], zoom_start=4)
    st_folium(m, width=700, height=500)
    st.subheader('Summary of Transactions')
    st.dataframe(pd.DataFrame(columns=[
        'Sender Account', 'total_sent', 'total_received', 'transactions_received', 'account_type', 'branch_involved'
    ]))
    st.subheader('Detailed Transactions List')
    st.dataframe(pd.DataFrame(columns=[
        'ID', 'Sender Account', 'Receiver Account', 'Amount', 'Date and Time',
        'Transaction Type', 'Purpose of Transaction'
    ]))
    st.subheader('Related Accounts')
    st.dataframe(pd.DataFrame(columns=[
        'Receiver Account', 'total_sent', 'total_received'
    ]))
