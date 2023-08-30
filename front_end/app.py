import streamlit as st
import pandas as pd

from modules import financial_plots as fp
from modules.chatbot import Message, Assistant
from modules.prompts import system_prompt

# Global variable to store uploaded file names
uploaded_files = []

# File Upload in the right column
def upload_file(col):
    col.header("Upload CSV Data")
    uploaded_file = col.file_uploader("Upload CSV Data (hidden label)", type="csv", help="Upload your financial data here.")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        uploaded_files.append(uploaded_file.name)
        col.write("Uploaded files:")
        for file_name in uploaded_files:
            col.write(file_name)
        return data
    return None

# Finance Dashboard in the main (left) column
def display_dashboard(data, col):
    col.header("Finance Dashboard")
    
    if data is not None:
        
        data = fp.clean_data(data)
        col.write("Raw Data Preview:")
        col.write(data.head())  # Display the first few rows of the uploaded CSV
        
        revenue_data = data[data['Item'] == 'Revenue']
        expense_data = data[data['Item'] != 'Revenue']
        
        # Display Monthly Revenue Trend
        left_col, right_col = col.columns(2)
        left_col.write("Monthly Revenue Trend")
        left_col.pyplot(fp.monthly_revenue_trend(revenue_data))
        
        # Display Monthly Expense Breakdown
        right_col.write("Monthly Expense Breakdown")
        right_col.pyplot(fp.monthly_expense_breakdown(expense_data))
        
        # Display Total Revenue vs. Total Expenses
        left_col, right_col = col.columns(2)
        left_col.write("Total Revenue vs. Total Expenses")
        left_col.pyplot(fp.total_revenue_vs_expenses(revenue_data, expense_data))
        
        # Display Cost Center-wise Expense Distribution
        right_col.write("Cost Center-wise Expense Distribution")
        right_col.pyplot(fp.cost_center_expense_distribution(expense_data))
        
        left_col, right_col = col.columns(2)
        # Display Monthly Net Profit/Loss (this will take the full width of the left column)
        left_col.write("Monthly Net Profit/Loss")
        left_col.pyplot(fp.monthly_net_profit_loss(revenue_data, expense_data))
    else:
        col.write("No data available. Please upload a CSV file.")



# Chat Interface in the right column below the file uploader
def chat_interface(col):
    col.header("Chat Interface")
    
    # Initialize the assistant if it's not in the session state
    if 'chat' not in st.session_state:
        st.session_state['chat'] = Assistant()
    
    # Initialize chat history if it's not in the session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    user_input = col.text_input("Ask a question about your data:")
    
    if user_input:
        messages = []
        # if there is no chat history, append the system prompt
        if len(st.session_state.chat_history) == 0:
            # don't store system prompt in chat history
            messages.append(Message(role="system", content=system_prompt.SYSTEM_PROMPT))

        # Append user input to chat history
        st.session_state.chat_history.append(("You", user_input))
        
        # Send user input to RetrievalAssistant and get response
        user_message = Message(role="user", content=user_input)
        messages.append(user_message)
        response_message = st.session_state['chat'].ask_assistant(messages)
        
        # Append assistant's response to chat history
        st.session_state.chat_history.append(("Assistant", response_message['content']))
        
    # Display chat history
    for chat in st.session_state.chat_history:
        col.write(f"{chat[0]}: {chat[1]}")
    
def main():
    st.set_page_config(layout="wide")
    st.markdown("<h1 style='text-align: center;'>Co-Pilot for CFO</h1>", unsafe_allow_html=True)

    # Create columns for the layout
    dashboard_col, chat_col = st.columns((3,1))

    data = upload_file(chat_col)
    display_dashboard(data, dashboard_col)
    chat_interface(chat_col)

def run():
    main()

if __name__ == "__main__":
    run()
