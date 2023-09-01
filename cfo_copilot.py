# Code refactored from https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps

import openai
import streamlit as st
import pandas as pd
import shutil
from codeinterpreterapi import File
from codeinterpreterapi import CodeInterpreterSession
from modules import financial_plots as fp
import asyncio
from utils import get_images, load_dotenv
import tempfile
import os
import io

#load_dotenv()

st.set_page_config(
        page_title="Co-Pilot for CFO",
        page_icon=":money_with_wings:",
        layout="wide",
        initial_sidebar_state="expanded"
    )

uploaded_files_list = []
data = []

with st.sidebar:
    
    st.title('🤖💵CFO Copilot')
    if 'OPENAI_API_KEY' in st.secrets:
        st.success('API key already provided!', icon='✅')
        openai.api_key = st.secrets['OPENAI_API_KEY']
    else:
        openai.api_key = st.text_input('Enter OpenAI API key:', type='password')
        if not (openai.api_key.startswith('sk-') and len(openai.api_key)==51):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    st.header("Upload Your Data")
    uploaded_file = st.file_uploader('data uploader', type='csv', help="Upload your financial data here.", label_visibility="hidden")
    if uploaded_file:
        #data = pd.read_csv(uploaded_file)
        #dfs.append(data)
        bytes_data = uploaded_file.read()
        data.append(bytes_data)
        uploaded_files_list.append(File(name=uploaded_file.name, content=bytes_data)) 



st.title("Your Finance Dashboard")
container = st.container()
if len(data) > 0:
        data_as_string = data[0].decode('utf-8')
        data_file_like = io.StringIO(data_as_string)
        df = pd.read_csv(data_file_like)

        cleaned = fp.clean_data(df)
        container.write("Raw Data Preview:")
        container.write(cleaned.head())
        left_col, right_col = container.columns(2)
        left_col.write("Monthly Revenue Trend")
        left_col.pyplot(fp.monthly_revenue_trend(cleaned.copy()))
        right_col.write("Monthly Expense Breakdown")
        right_col.pyplot(fp.monthly_expense_breakdown(cleaned.copy()))
        left_col, right_col = container.columns(2)
        left_col.write("Total Revenue vs. Total Expenses")
        left_col.pyplot(fp.total_revenue_vs_expenses(cleaned.copy()))
        right_col.write("Monthly Net Profit/Loss")
        right_col.pyplot(fp.monthly_net_profit_loss(cleaned.copy()))

else:
    container.write("No data available. Please upload a CSV file.")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Question about your financial data?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.spinner("Thinking..."):
        with CodeInterpreterSession(model="gpt-4-0613") as session:
            response = session.generate_response_sync(prompt, files=uploaded_files_list)

            with st.chat_message("assistant"):
                st.write(response.content)

                # Showing Results
                for _file in response.files:
                    st.image(_file.get_image(), caption=prompt, use_column_width=True)

                # Allowing the download of the results
                if len(response.files) == 1:
                    st.download_button(
                        "Download Results",
                        response.files[0].content,
                        file_name=response.files[0].name,
                        use_container_width=True,
                    )
                elif len(response.files) > 1:
                    target_path = tempfile.mkdtemp()
                    for _file in response.files:
                        _file.save(os.path.join(target_path, _file.name))

                    zip_path = os.path.join(os.path.dirname(target_path), "archive")
                    shutil.make_archive(zip_path, "zip", target_path)

                    with open(zip_path + ".zip", "rb") as f:
                        st.download_button(
                            "Download Results",
                            f,
                            file_name="archive.zip",
                            use_container_width=True,
                        )

        #message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": response.content})