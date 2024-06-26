import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import streamlit.components.v1 as components


from graphs.timeline import display_transactions
from graphs.sankey import generate_sankey
from graphs.pie import generate_pie_chart
from graphs.ego import ego
from graphs.map import transaction_map

from transformations.summary import summary_of_transactions, transactions

PATH = 'data/Data.xlsx'


@st.cache_data
def load_dataset(PATH):
    return pd.read_excel(PATH)


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
df = load_dataset(PATH)

combined_names = sorted(set(df['Sender Name']).union(set(df['Receiver Name'])))
combined_phone_numbers = sorted(
    set(df['Sender Phone Number']).union(set(df['Receiver Phone Number'])))
combined_acc_no = sorted(
    set(df['Sender Account']).union(set(df['Receiver Account'])))

with st.sidebar:
    st.title('Bank Transactions Dashboard')
    names = st.multiselect('Select a name', combined_names)
    phone_numbers = st.multiselect(
        'Select a phone number', combined_phone_numbers)
    acc_no = st.multiselect('Select an account number', combined_acc_no)

filtered_df = df.copy()

filtered_dfs = []

if names:
    filtered_df_1 = filtered_df[filtered_df['Sender Name'].isin(
        names) | filtered_df['Receiver Name'].isin(names)]
    filtered_dfs.append(filtered_df_1)

if phone_numbers:
    filtered_df_2 = filtered_df[filtered_df['Sender Phone Number'].isin(
        phone_numbers) | filtered_df['Receiver Phone Number'].isin(phone_numbers)]
    filtered_dfs.append(filtered_df_2)

if acc_no:
    filtered_df_3 = filtered_df[filtered_df['Sender Account'].isin(
        acc_no) | filtered_df['Receiver Account'].isin(acc_no)]
    filtered_dfs.append(filtered_df_3)

# Concatenate all filtered dataframes, avoiding duplicate columns
if filtered_dfs:
    filtered_df = pd.concat(filtered_dfs, axis=0).loc[:, ~pd.concat(
        filtered_dfs, axis=0).columns.duplicated()]


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
                <div class="metric-title">No. of Involved</div>
                <div class="metric-value">{len(np.unique(
    np.concatenate([filtered_df['Sender Account'].unique(), filtered_df['Receiver Account'].unique()])
        ))}</div>
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
        st.subheader('Ego Graph')
        G = ego(filtered_df)

        # Save the network to an HTML file
        html_file_path = 'network_graph.html'
        G.write_html(html_file_path)
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Display the HTML content in Streamlit
        components.html(html_content, height=450, width=700)

    display_transactions(filtered_df)

    summary_of_transactions(df, filtered_df)
    transactions(filtered_df)


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
                <div class="metric-title">No. of Involved</div>
                <div class="metric-value"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.warning(
        'Please enter names or phone numbers, or account numbers to view the data.')
