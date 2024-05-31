import pandas as pd
import streamlit as st

# Function to add icons based on transaction types


def add_transaction_type_icons(transaction_type):
    if transaction_type == 'Debit':
        return f"🔴 {transaction_type}"
    elif transaction_type == 'Credit':
        return f"🟢 {transaction_type}"
    else:
        return transaction_type

# Function to add icons based on purposes of transactions


def add_purpose_icons(purpose):
    if 'Salary' in purpose:
        return f"💼 {purpose}"
    elif 'Refund' in purpose:
        return f"💸 {purpose}"
    elif 'Purchase' in purpose:
        return f"🛒 {purpose}"
    elif 'Payment' in purpose:
        return f"💳 {purpose}"
    elif 'Transfer' in purpose:
        return f"💰 {purpose}"
    elif 'Gift' in purpose:
        return f"🎁 {purpose}"
    else:
        return purpose

# Function to generate the summary of transactions


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
        branches_involved_received = received_transactions.groupby('Sender Account Branch')[
            'Amount'].sum().to_dict() if len(received_transactions) > 0 else '-'

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

    # Ensure columns exist before applying transformations
    if 'Total Sent' in summary_df.columns:
        summary_df['Total Sent'] = summary_df['Total Sent'].apply(
            lambda x: f'💸 {x}')
    else:
        st.error("Column 'Total Sent' not found in DataFrame")

    if 'Total Received' in summary_df.columns:
        summary_df['Total Received'] = summary_df['Total Received'].apply(
            lambda x: f'💰 {x}')
    else:
        st.error("Column 'Total Received' not found in DataFrame")

    if 'No. of Transactions Received' in summary_df.columns:
        summary_df['No. of Transactions Received'] = summary_df['No. of Transactions Received'].apply(
            lambda x: f'📥 {x}')
    else:
        st.error("Column 'No. of Transactions Received' not found in DataFrame")

    if 'No. of Transactions Sent' in summary_df.columns:
        summary_df['No. of Transactions Sent'] = summary_df['No. of Transactions Sent'].apply(
            lambda x: f'📤 {x}')
    else:
        st.error("Column 'No. of Transactions Sent' not found in DataFrame")

    # Convert branch involvement dictionaries to JSON strings
    if 'Branches Involved (Sent)' in summary_df.columns:
        summary_df['Branches Involved (Sent)'] = summary_df['Branches Involved (Sent)'].apply(
            lambda x: str(x) if isinstance(x, dict) else x)
    else:
        st.error("Column 'Branches Involved (Sent)' not found in DataFrame")

    if 'Branches Involved (Received)' in summary_df.columns:
        summary_df['Branches Involved (Received)'] = summary_df['Branches Involved (Received)'].apply(
            lambda x: str(x) if isinstance(x, dict) else x)
    else:
        st.error("Column 'Branches Involved (Received)' not found in DataFrame")

    st.subheader('Summary of Transactions')
    st.dataframe(summary_df)


def transactions(df):
    st.subheader('Detailed Transactions List')
    df = df[[
        'ID', 'Sender Account', 'Sender Name', 'Receiver Account', 'Receiver Name', 'Amount', 'Date and Time',
        'Transaction Type', 'Purpose of Transaction'
    ]].copy()

    # Apply icons to transaction types and purposes
    df.loc[:, 'Transaction Type'] = df['Transaction Type'].apply(
        add_transaction_type_icons)
    df.loc[:, 'Purpose of Transaction'] = df['Purpose of Transaction'].apply(
        add_purpose_icons)

    st.dataframe(df)
