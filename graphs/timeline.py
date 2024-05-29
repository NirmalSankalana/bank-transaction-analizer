import streamlit as st
import pandas as pd
import plotly.graph_objects as go


@st.cache_resource
def preprocess_candlestick_data(df):
    # Calculate low and close values for sender transactions
    df['low_sender'] = df['Sender Current Account Balance'] - df['Amount']
    df['close_sender'] = df['Sender Current Account Balance'] - df['Amount']
    grouped_sender = df.groupby([
        pd.Grouper(key='Date and Time', freq='D'),
        'Sender Account',
        'Sender Name',
        'Transaction Type'
    ]).agg(
        open=('Sender Current Account Balance', 'first'),
        high=('Sender Current Account Balance', 'max'),
        low=('low_sender', 'min'),
        close=('close_sender', 'last')
    ).reset_index()
    grouped_sender.rename(
        columns={'Sender Account': 'Account', 'Sender Name': 'Name'}, inplace=True)

    # Calculate low and close values for receiver transactions
    df['high_receiver'] = df['Receiver Current Account Balance'] + df['Amount']
    df['close_receiver'] = df['Receiver Current Account Balance'] + df['Amount']
    grouped_receiver = df.groupby([
        pd.Grouper(key='Date and Time', freq='D'),
        'Receiver Account',
        'Receiver Name',
        'Transaction Type'
    ]).agg(
        open=('Receiver Current Account Balance', 'first'),
        high=('high_receiver', 'max'),
        low=('Receiver Current Account Balance', 'min'),
        close=('close_receiver', 'last')
    ).reset_index()
    grouped_receiver.rename(
        columns={'Receiver Account': 'Account', 'Receiver Name': 'Name'}, inplace=True)

    concatenated_df = pd.concat([grouped_sender, grouped_receiver])

    # st.write(concatenated_df)

    return concatenated_df


def display_transactions(filtered_df):
    st.subheader('Transaction Timelines')

    # Convert 'Date and Time' to datetime
    filtered_df['Date and Time'] = pd.to_datetime(filtered_df['Date and Time'])

    # Preprocess data for candlestick chart
    candlestick_data = preprocess_candlestick_data(filtered_df)

    # Get unique accounts
    unique_accounts = filtered_df['Sender Account'].unique()

    # Initialize column index
    col_index = 0
    cols = None

    # Loop through each account and create a candlestick chart
    for account in unique_accounts:
        if col_index % 4 == 0:
            # Create a new row with 4 columns
            cols = st.columns(4)

        # Filter data for the current account
        account_data = candlestick_data[candlestick_data['Account'] == account]

        # Create Plotly figure
        fig = go.Figure()

        # Add candlestick for sent transactions
        sent_data = account_data[account_data['Transaction Type'] == 'Credit']
        fig.add_trace(go.Candlestick(
            x=sent_data['Date and Time'],
            open=sent_data['open'],
            high=sent_data['high'],
            low=sent_data['low'],
            close=sent_data['close'],
            name='Sent Transactions',
            increasing_line_color='red',
            decreasing_line_color='red'
        ))

        # Add candlestick for received transactions
        received_data = account_data[account_data['Transaction Type'] == 'Debit']
        fig.add_trace(go.Candlestick(
            x=received_data['Date and Time'],
            open=received_data['open'],
            high=received_data['high'],
            low=received_data['low'],
            close=received_data['close'],
            name='Received Transactions',
            increasing_line_color='green',
            decreasing_line_color='green'
        ))

        name = candlestick_data[candlestick_data["Account"]
                                == account]["Name"].iloc[0]

        # Update layout
        fig.update_layout(
            title=f'Transaction Timelines for {name}',
            xaxis_title='Date',
            yaxis_title='Transaction Amount',
            xaxis_rangeslider_visible=False,
            template='plotly_dark'
        )

        # Display chart in the current column
        cols[col_index % 4].plotly_chart(fig, use_container_width=True)

        # Increment column index
        col_index += 1
