# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import streamlit as st
import luana_engine
from luana_engine import interpreter
import os
from luana_engine.utils import load_dotenv, plot_files
from sodapy import Socrata
import pandas as pd
import plotly.io as pio
import json

load_dotenv()


metric_prompt_template = """and it's delta over last time period in percentage, return a json obeject of schema: {"value": "", "delta": ""}, no explaination, return the json object directly in your response."""


# set color palette
custom_colors = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
custom_template = {"layout": {"colorway": custom_colors}}
pio.templates["custom_template"] = custom_template
pio.templates.default = "custom_template"


st.set_page_config(
    page_title="Co-Pilot for CFO",
    page_icon=":money_with_wings:",
    layout="wide",
    initial_sidebar_state="expanded",
)


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
        st.markdown("7. Save the table to a csv file")

    elif data == "SanFrancisco City Budget":
        os.environ["data"] = ".data/sf_budget.csv"
        st.markdown("Sample questions you can ask about City Budget")
        st.markdown("1. show me the total budget year over year")
        st.markdown("2. what contributed to the budget decrease in year 2021?")
        st.markdown("3. give me a budget breakdown in 2021")


st.title("Your Finance Dashboard")
st.subheader("Automated analysis, insights and answers to your questions instantly")

# initialize the agent
if "agent" not in st.session_state:
    st.session_state["agent"] = interpreter.Interpreter()
    st.session_state["agent"].use_azure = False #os.environ['USE_AZURE']


# download data from socrata
@st.cache_data
def download_data():
    if not os.path.exists(".data/sf_budget.csv"):
        # Unauthenticated client only works with public data sets. Note 'None'
        # in place of application token, and no username or password:
        client = Socrata("data.sfgov.org", None)
        results = client.get("xdgd-c79v", limit=2000)
        # Convert to pandas DataFrame
        results_df = pd.DataFrame.from_records(results)
        # store df to file
        results_df.to_csv(".data/sf_budget.csv", index=False)


download_data()


@st.cache_resource
def get_metrics():
    all_metrics_data = {}
    all_files = []
    messages, _ = st.session_state["agent"].chat(
        "Analyze the data and come up with 1-4 key metrics you can calculate to show value, and delta over last time period. "
        + "Tell me the metric names directly in one sentence, comma seperated, without any explanation, ",
        return_messages=True,
        show_thinking=False,
    )
    print("messages inside metrics", messages)
    metrics = messages[-1]["content"].split(",")
    num_metrics = len(metrics)

    if num_metrics > 0:
        for i in range(num_metrics):
            files = st.session_state["agent"].chat(
                f"now plot the metric {metrics[i]} over time, save the plot as {metrics[i]}.json using plotly",
                return_messages=False,
                plot=False,
                show_thinking=False,
            )
            all_files.append(files)
            messages, _ = st.session_state["agent"].chat(
                "now calculate the value of " + metrics[i] + metric_prompt_template,
                return_messages=True,
                show_thinking=False,
            )
            # parse last message as json object
            start_pos = messages[-1]["content"].find("{")
            end_pos = messages[-1]["content"].rfind("}") + 1

            # Extract the JSON object string
            json_str = messages[-1]["content"][start_pos:end_pos]

            # Parse the JSON object string to a Python dictionary
            metric_data = json.loads(json_str)
            value = metric_data["value"]
            value = "{:.2f}".format(value)
            delta = metric_data["delta"]
            # convert delta to show 2 decimal places
            delta = "{:.2f}".format(delta)
            all_metrics_data[metrics[i]] = {"value": value, "delta": delta}
    else:
        print("No metrics found")

    return all_metrics_data, num_metrics, all_files


all_metrics_data, num_metrics, all_files = get_metrics()
metric_coponents = st.columns(num_metrics)
i = 0
for key, value in all_metrics_data.items():
    metric_coponents[i].metric(
        label=key,
        value=value["value"],
        delta=value["delta"] + "%",
    )
    i += 1

dashboard1, dashboard2 = st.columns(2, gap="large")
# plot file alternatively in dashboard 1 and 2
idx = 0
for file in all_files:
    if idx % 2 == 0:
        plot_files(file, dashboard1)
    else:
        plot_files(file, dashboard2)
    idx += 1


@st.cache_resource
def get_summary():
    messages, _ = st.session_state["agent"].chat(
        "Based on the key metrics, generate a executive summary and recommendations in 2-3 sentences",
        return_messages=True,
        plot=False,
        show_thinking=False,
    )
    return messages[-1]["content"]


summary = get_summary()
st.title("**Executive Summary:**")
st.markdown(summary)
st.markdown("**Got questions? Ask here:**")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if message["content"] != "":
        if message["role"] == "user":
            st.chat_message("user", avatar="🙋‍♂️").markdown(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assitant", avatar="📈").markdown(message["content"])

if prompt := st.chat_input("Question about your financial data?"):
    st.chat_message("user", avatar="🙋‍♂️").markdown(prompt)
    with st.chat_message("assitant", avatar="📈"):
        messages, files = st.session_state["agent"].chat(
            prompt,
            return_messages=True,
            plot=True,
            show_thinking=True,
            store_history=True,
        )
        st.session_state.messages = messages
