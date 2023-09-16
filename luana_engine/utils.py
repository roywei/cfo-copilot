import json
import os
from os.path import join, dirname
import openai
from .prompts.output_file_check import output_file_check_prompt
import streamlit as st


def load_dotenv():
    # find the .env file from parent directory
    dotenv_path = join(dirname(__file__), "../.env")
    # read each line and assign env var name and value split by '='
    print("loading env file from: ", dotenv_path)
    # check if file exists
    if os.path.exists(dotenv_path):
        for line in open(dotenv_path):
            var = line.strip().split("=")
            if len(var) == 2:
                key, value = var[0].strip(), var[1].strip()
                # set the env var
                os.environ[key] = value
    else:
        print("WARNING: .env file not found")


def merge_deltas(original, delta):
    """
    Pushes the delta into the original and returns that.

    Great for reconstructing OpenAI streaming responses -> complete message objects.
    """
    for key, value in delta.items():
        if isinstance(value, dict):
            if key not in original:
                original[key] = value
            else:
                merge_deltas(original[key], value)
        else:
            if key in original:
                original[key] += value
            else:
                original[key] = value
    return original


def parse_partial_json(s):
    # Attempt to parse the string as-is.
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass

    # Initialize variables.
    new_s = ""
    stack = []
    is_inside_string = False
    escaped = False

    # Process each character in the string one at a time.
    for char in s:
        if is_inside_string:
            if char == '"' and not escaped:
                is_inside_string = False
            elif char == "\n" and not escaped:
                char = "\\n"  # Replace the newline character with the escape sequence.
            elif char == "\\":
                escaped = not escaped
            else:
                escaped = False
        else:
            if char == '"':
                is_inside_string = True
                escaped = False
            elif char == "{":
                stack.append("}")
            elif char == "[":
                stack.append("]")
            elif char == "}" or char == "]":
                if stack and stack[-1] == char:
                    stack.pop()
                else:
                    # Mismatched closing character; the input is malformed.
                    return None

        # Append the processed character to the new string.
        new_s += char

    # If we're still inside a string at the end of processing, we need to close the string.
    if is_inside_string:
        new_s += '"'

    # Close any remaining open structures in the reverse order that they were opened.
    for closing_char in reversed(stack):
        new_s += closing_char

    # Attempt to parse the modified string as JSON.
    try:
        return json.loads(new_s)
    except json.JSONDecodeError:
        # If we still can't parse the string as JSON, return None to indicate failure.
        return None


def get_file_modifications(code: str, retry: int = 2):
    if retry < 1:
        return None

    prompt = output_file_check_prompt.format(code=code)
    messages = [{"role": "user", "content": prompt}]
    print(messages)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=False,
        temperature=0.03,
    )

    try:
        result = json.loads(response["choices"][0]["message"]["content"])
    except json.JSONDecodeError:
        result = ""
    if not result or not isinstance(result, dict) or "modifications" not in result:
        return get_file_modifications(code, llm, retry=retry - 1)
    return result["modifications"]


@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def plot_files(file, component=None):
        if file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg"):
            image = Image.open(file)
            if component:
                component.image(image)
            else:
                st.image(image)
        elif file.endswith(".json"):
            import plotly

            fig = plotly.io.read_json(file)
            if component:
                component.plotly_chart(fig, use_container_width=True)
            else:
                st.plotly_chart(fig, use_container_width=True)
        elif file.endswith(".csv"):
            import pandas as pd

            df = pd.read_csv(file)
            # show dataframe
            st.dataframe(df, use_container_width=True)
            csv = convert_df(df)
            # strip directy path from file name
            file_name = file.split("/")[-1]
            st.download_button(
                "Press to Download: " + file_name,
                csv,
                file_name,
                "text/csv",
                key=file_name,
            )
        else:
            print("unsupported file type:", file)
