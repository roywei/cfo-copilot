# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import streamlit as st
from luana_engine import interpreter
import os
from streamlit_elements import elements, mui, html
from luana_engine.utils import load_dotenv
load_dotenv()

st.set_page_config(
        page_title="Co-Pilot for CFO",
        page_icon=":money_with_wings:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

uploaded_files_list = []
data = []

with st.sidebar:
    st.title("Select Data Source")
    # drop down menu for selecting the data
    data = st.selectbox(
        "",
        ["Company Finance", "SanFrancisco City Budget"],
    )
    if data == "Company Finance":
        os.environ['data'] = ".data/finance.csv"
        st.markdown("Sample questions you can ask about Company Finance:")
        st.markdown("1. What is the total revenue in September?")
        st.markdown("2. Show me the revenue month over month")
        st.markdown("3. Show me July cost breakdown by category")
        st.markdown("4. Give me a trend on consulting fees")
        st.markdown("5. Show me my P&L month over month")
        st.markdown("6. Show me my profit margin month over month")

    elif data == "SanFrancisco City Budget":
        os.environ['data'] = ".data/Budget.csv"
        st.markdown("Sample questions you can ask about City Budget")
        st.markdown("1. show me the total budget year over year")
        st.markdown("2. what contributed to the budget decrease in year 2021?")
        st.markdown("3. give me a budget breakdown in 2021")



st.title("Luana.AI: Co-Pilot for CFO ")

if "agent" not in st.session_state:
    st.session_state["agent"] = interpreter.Interpreter()


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["role"] == "user" or message["role"] == "assistant" and "Here is" in message["content"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Question about your financial data?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assitant"):
        messages = st.session_state["agent"].chat(prompt, return_messages=True)
        st.session_state.messages = messages