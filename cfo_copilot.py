# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import streamlit as st
from luana_engine import interpreter
import os
from luana_engine.utils import load_dotenv
from sodapy import Socrata
import pandas as pd
from luana_engine import financial_plots as fp
import plotly.io as pio

load_dotenv()



# set color palette
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
custom_template = {
    'layout': {
        'colorway': custom_colors
    }
}
pio.templates["custom_template"] = custom_template
pio.templates.default = "custom_template"
   

st.set_page_config(
    page_title="Co-Pilot for CFO",
    page_icon=":money_with_wings:",
    layout="wide",
    initial_sidebar_state="expanded",
)

uploaded_files_list = []
data = []

# download data
if not os.path.exists(".data/sf_budget.csv"):
    # Unauthenticated client only works with public data sets. Note 'None'
    # in place of application token, and no username or password:
    client = Socrata("data.sfgov.org", None)
    results = client.get("xdgd-c79v", limit=2000)
    # Convert to pandas DataFrame
    results_df = pd.DataFrame.from_records(results)
    # store df to file
    results_df.to_csv(".data/sf_budget.csv", index=False)


with st.sidebar:
    st.title("Luana.AI: Co-Pilot for CFO")
    # drop down menu for selecting the data
    data = st.selectbox(
        "Select Data Source",
        ["Company Finance", "SanFrancisco City Budget"],
    )
    if data == "Company Finance":
        os.environ["data"] = ".data/finance.csv"
        st.markdown("Sample questions you can ask about Company Finance:")
        st.markdown("1. What is the total revenue in September?")
        st.markdown("2. Show me the revenue month over month")
        st.markdown("3. Show me July cost breakdown by category")
        st.markdown("4. Give me a trend on consulting fees")
        st.markdown("5. Show me my P&L month over month")
        st.markdown("6. Show me my profit margin month over month")

    elif data == "SanFrancisco City Budget":
        os.environ["data"] = ".data/sf_budget.csv"
        st.markdown("Sample questions you can ask about City Budget")
        st.markdown("1. show me the total budget year over year")
        st.markdown("2. what contributed to the budget decrease in year 2021?")
        st.markdown("3. give me a budget breakdown in 2021")


st.title("You Finance Dashboard")
key_metric1, key_metric2, key_metric3, key_metric4 = st.columns(4)
key_metric1.metric(label="Revenue", value="1.2M", delta="0.5M")
key_metric2.metric(label="Revenue Growth", value="30%", delta="10%")
key_metric3.metric(label="Profit Margin", value="20%", delta="3%")
key_metric4.metric(label="Operating Expense Ratio (OER)", value="30%", delta="-5%")

with st.spinner("Loading data..."):
    # read the data
    df = pd.read_csv(os.environ["data"])
    cleaned_data = fp.clean_data(df)


dashboard, chat_panel = st.columns(2, gap="large")
dashboard.plotly_chart(fp.monthly_revenue_trend(cleaned_data.copy()))
dashboard.plotly_chart(fp.monthly_net_profit_loss(cleaned_data.copy()))

if "agent" not in st.session_state:
    st.session_state["agent"] = interpreter.Interpreter()


if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:
    if (
        message["role"] == "user"
        or message["role"] == "assistant"
        and message["content"] != ""
    ):
        chat_panel.chat_message(message["role"]).markdown(message["content"])

if prompt := st.chat_input("Question about your financial data?"):
    chat_panel.chat_message("user").markdown(prompt)
    with chat_panel.chat_message("assitant", avatar="📊"):
        messages = st.session_state["agent"].chat(prompt, return_messages=True)
        st.session_state.messages = messages
