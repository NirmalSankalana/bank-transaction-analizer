import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder


def summary_of_transactions(df, filtered_df):
    summary_data = []

    # Unique accounts
    accounts = pd.unique(
        filtered_df[['Sender Account', 'Receiver Account']].values.ravel('K'))

    for account in accounts:
        account_type = df.loc[df['Sender Account']
                              == account, 'Sender Account Type'].values
        account_name = df.loc[df['Sender Account']
                              == account, 'Sender Name'].values

        if len(account_type) == 0:
            account_type = df.loc[df['Receiver Account']
                                  == account, 'Receiver Account Type'].values
            account_name = df.loc[df['Receiver Account']
                                  == account, 'Receiver Name'].values

        account_type = account_type[0] if len(account_type) > 0 else 'Unknown'
        account_name = account_name[0] if len(account_name) > 0 else 'Unknown'

        sent_transactions = df[df['Sender Account'] == account]
        received_transactions = df[df['Receiver Account'] == account]

        total_sent = sent_transactions['Amount'].sum()
        total_received = received_transactions['Amount'].sum()

        number_of_transactions_received = received_transactions.shape[0]
        number_of_transactions_sent = sent_transactions.shape[0]

        branches_involved_sent = sent_transactions.groupby('Receiver Account Branch')[
            'Amount'].sum().to_dict() if len(sent_transactions) > 0 else '-'
        branches_involved_received = received_transactions.groupby(
            'Sender Account Branch')['Amount'].sum().to_dict() if len(received_transactions) > 0 else '-'

        summary_data.append({
            'Account Number': account,
            'Account Name': account_name,
            'Account Type': account_type,
            'Total Sent': total_sent,
            'Total Received': total_received,
            'No. of Transactions Received': number_of_transactions_received,
            'No. of Transactions Sent': number_of_transactions_sent,
            'Branches Involved (Sent)': branches_involved_sent,
            'Branches Involved (Received)': branches_involved_received,
        })

    summary_df = pd.DataFrame(summary_data)

    # Add icons for total sent and received
    summary_df['Total Sent'] = summary_df['Total Sent'].apply(
        lambda x: f'💸 {x}')
    summary_df['Total Received'] = summary_df['Total Received'].apply(
        lambda x: f'💰 {x}')

    # Add icons for transaction counts
    summary_df['No. of Transactions Received'] = summary_df['No. of Transactions Received'].apply(
        lambda x: f'📥 {x}')
    summary_df['No. of Transactions Sent'] = summary_df['No. of Transactions Sent'].apply(
        lambda x: f'📤 {x}')

    # Convert branch involvement dictionaries to JSON strings
    summary_df['Branches Involved (Sent)'] = summary_df['Branches Involved (Sent)'].apply(
        lambda x: str(x) if isinstance(x, dict) else x)
    summary_df['Branches Involved (Received)'] = summary_df['Branches Involved (Received)'].apply(
        lambda x: str(x) if isinstance(x, dict) else x)

    st.subheader('Summary of Transactions')
    AgGrid(summary_df)


def transactions(df):
    st.subheader('Detailed Transactions List')
    df = df[[
        'ID', 'Sender Account', 'Sender Name', 'Receiver Account', 'Receiver Name', 'Amount', 'Date and Time',
        'Transaction Type', 'Purpose of Transaction'
    ]]
    AgGrid(df)
