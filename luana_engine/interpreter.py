from .utils import merge_deltas, parse_partial_json
from .code_interpreter import CodeInterpreter
from .python_interpreter import PythonInterpreter
from .prompts import system_prompt
import os
import time
import platform
import openai
import getpass
import tokentrim as tt
from .utils import load_dotenv
import streamlit as st
from .utils import get_file_modifications
import shutil
from .utils import plot_files
from .prompts.generate_functions import finance_data_functions, city_budget_functions

# Function schema for gpt-4
function_schema = {
    "name": "run_code",
    "description": "Executes code on the user's machine and returns the output, if any plots are generated, only return the filenames, do not show the plots.",
    "parameters": {
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "The programming language",
                "enum": ["python", "shell", "applescript", "javascript", "html"],
            },
            "code": {"type": "string", "description": "The code to execute"},
        },
        "required": ["language", "code"],
    },
}

# Message for when users don't have an OpenAI API key.
missing_api_key_message = """> OpenAI API key not found

To use `GPT-4` (recommended) please provide an OpenAI API key.

To use `Code-Llama` (free but less capable) press `enter`.
"""

# Message for when users don't have an OpenAI API key.
missing_azure_info_message = """> Azure OpenAI Service API info not found

To use `GPT-4` (recommended) please provide an Azure OpenAI API key, a API base, a deployment name and a API version.

To use `Code-Llama` (free but less capable) press `enter`.
"""

confirm_mode_message = """
**Open Interpreter** will require approval before running code. Use `interpreter -y` to bypass this.

Press `CTRL-C` to exit.
"""

pre_load_function_mapping = {
    ".data/finance.csv": finance_data_functions,
    ".data/sf_budget.csv": city_budget_functions,
}


class Interpreter:
    def __init__(self):
        info = self.get_info_for_system_message()
        self.temperature = 0.001
        self.api_key = None
        self.auto_run = False
        self.local = False
        self.model = os.environ.get("MODEL", "gpt-4")
        self.debug_mode = os.environ.get("DEBUG_MODE", False)
        # Azure OpenAI
        self.use_azure = False
        self.azure_api_base = None
        self.azure_api_version = None
        self.azure_deployment_name = None

        # Get default system message

        self.system_message = system_prompt.OPEN_SYSTEM_PROMPT
        self.system_message += "\n\n" + info
        self.messages = []
        # Store Code Interpreter instances for each language
        self.code_interpreters = {}
        self.last_ran_code = None
        self.additional_system_message = None
        self.data_path = None
        self.think_step = 0
        self.chat_history = []
        self.output_files = []
        # delete all files in .output folder but keep the folder
        """
        dir_path = ".output"
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        """

    def get_info_for_system_message(self):
        """
        Gets relevent information for the system message.
        """

        info = ""

        # Add user info
        username = getpass.getuser()
        current_working_directory = os.getcwd()
        operating_system = platform.system()

        info += f"[User Info]\nName: {username}\nCWD: {current_working_directory}\nOS: {operating_system}"

        return info

    def reset(self):
        self.messages = []
        self.code_interpreters = {}

    def load(self, messages):
        self.messages = messages

    def chat(
        self,
        message=None,
        return_messages=False,
        plot=False,
        show_thinking=False,
        store_history=False,
    ):
        # Connect to an LLM (an large language model)
        if not self.local:
            # gpt-4
            self.verify_api_key()
        self.output_files = []
        print("Inside chat now")
        if message:
            # If it was, we respond non-interactivley
            self.messages.append({"role": "user", "content": message})
            if store_history:
                self.chat_history.append({"role": "user", "content": message})
            self.respond(
                plot=plot, show_thinking=show_thinking, store_history=store_history
            )

        if return_messages:
            return (
                self.chat_history if self.chat_history else self.messages,
                self.output_files,
            )
        else:
            return self.output_files

    def verify_api_key(self):
        """
        Makes sure we have an OPENAI_API_KEY.
        """
        if self.use_azure:
            all_env_available = (
                "AZURE_OPENAI_KEY1" in os.environ
                and "AZURE_API_BASE" in os.environ
                and "AZURE_API_VERSION" in os.environ
                and "AZURE_DEPLOYMENT_NAME" in os.environ
            )
            if all_env_available:
                self.api_key = os.environ["AZURE_OPENAI_KEY1"]
                print(self.api_key)
                self.azure_api_base = os.environ["AZURE_API_BASE"]
                print(self.azure_api_base)
                self.azure_api_version = os.environ["AZURE_API_VERSION"]
                print(self.azure_api_version)
                self.azure_deployment_name = os.environ["AZURE_DEPLOYMENT_NAME"]
                print(self.azure_deployment_name)
            else:
                # TODO: guide user to configure azure
                print(missing_azure_info_message)
            load_dotenv()
            openai.api_type = "azure"
            openai.api_base = self.azure_api_base
            openai.api_version = self.azure_api_version
            openai.api_key = self.api_key
        else:
            print("using openai")
            load_dotenv()
            openai.api_key = os.environ["OPENAI_API_KEY"]

    def respond(self, plot=False, show_thinking=False, store_history=False):
        # Add relevant info to system_message
        # (e.g. current working directory, username, os, etc.)
        # info = self.get_info_for_system_message()

        # system_message = self.system_message + "\n\n" + info
        self.think_step += 1
        if not self.additional_system_message or self.data_path != os.environ.get(
            "data", ".data/finance.csv"
        ):
            import pandas as pd

            df = pd.read_csv(os.environ.get("data", ".data/finance.csv"))
            description = df.describe().to_string()
            first_rows = df.head(5).to_string()
            self.additional_system_message = (
                "The data is located locally in current directory at "
                + os.environ.get("data", ".data/finance.csv")
                + " Remember this is finance data per accounting format. Remove duplicate rows if necessary. Fill nan values with 0, convert string numbers to float and remove comma."
                + "When you calculate Revenue or Profit, remember to convert revenue sum to positive."
                + "Remember Revenue is not cost nor expense, think carefully about what to include and exclude in the result."
                + "Try to use plot or table to present your result, decide on the best plot or chart type for financial reporting, use bar chart for breakdown comparison."
                + "Remember to only use plotly for plots, never show the plot, always save output using plotly.io.write_json to .output/ folder in json format, finance dashboard can only read from output files."
                + "When you decide to output a table, ask the user if they want to export it, if so, save it to .output/ folder in csv format"
                + "Don't tell the user where you stored the output data, tell the user it will be displayed on the finance dashboard"
                "The data description is "
                + description
                + " and the first 5 rows are "
                + first_rows
            )

        messages = tt.trim(
            self.messages,
            self.model,
            trim_ratio=0.5,
            system_message=self.system_message
            + pre_load_function_mapping[os.environ.get("data", ".data/finance.csv")]
            + self.additional_system_message,
        )

        if self.debug_mode:
            print("\n", "Sending `messages` to LLM:", "\n")
            print(messages)
            print()

        # Initialize message, function call trackers, and active block
        self.messages.append({})
        in_function_call = False

        expander = None
        process_box = None
        if show_thinking:
            expander = st.expander("Show Thinking Step " + str(self.think_step))
            process_box = expander.empty()

        for _ in range(3):  # 3 retries
            try:
                if self.use_azure:
                    response = openai.ChatCompletion.create(
                        engine=self.azure_deployment_name,
                        messages=messages,
                        functions=[function_schema],
                        temperature=self.temperature,
                        stream=True,
                    )
                else:
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=messages,
                        functions=[function_schema],
                        stream=True,
                        temperature=self.temperature,
                    )

                break
            except openai.error.RateLimitError:
                # Rate limit hit. Retrying in 3 seconds
                time.sleep(5)
        else:
            raise openai.error.RateLimitError("RateLimitError: Max retries reached")

        for chunk in response:
            if self.use_azure and ('choices' not in chunk or len(chunk['choices']) == 0):
                continue

            else:
                delta = chunk["choices"][0]["delta"]

            # Accumulate deltas into the last message in messages
            self.messages[-1] = merge_deltas(self.messages[-1], delta)

            if "function_call" in self.messages[-1]:
                if in_function_call == False:
                    pass

                in_function_call = True
                if "arguments" in self.messages[-1]["function_call"]:
                    arguments = self.messages[-1]["function_call"]["arguments"]
                    new_parsed_arguments = parse_partial_json(arguments)
                    if new_parsed_arguments:
                        self.messages[-1]["function_call"][
                            "parsed_arguments"
                        ] = new_parsed_arguments
            else:
                in_function_call = False
                if show_thinking:
                    # stream thinking process
                    process_box.markdown(self.messages[-1]["content"])

            if chunk["choices"][0]["finish_reason"]:
                if chunk["choices"][0]["finish_reason"] == "function_call":
                    if self.debug_mode:
                        print("Running function:")
                        print(self.messages[-1])
                        print("---")
                        if show_thinking:
                            process_box.markdown("Running function:")
                            process_box.code(
                                self.messages[-1]["function_call"]["parsed_arguments"][
                                    "code"
                                ],
                                language=self.messages[-1]["function_call"][
                                    "parsed_arguments"
                                ]["language"],
                            )

                    if "parsed_arguments" not in self.messages[-1]["function_call"]:
                        self.messages.append(
                            {
                                "role": "function",
                                "name": "run_code",
                                "content": """Your function call could not be parsed. Please use ONLY the `run_code` function, which takes two parameters: `code` and `language`. Your response should be formatted as a JSON.""",
                            }
                        )

                        self.respond(
                            plot=plot,
                            show_thinking=show_thinking,
                            store_history=store_history,
                        )
                        return
                    language = self.messages[-1]["function_call"]["parsed_arguments"][
                        "language"
                    ]
                    if language not in self.code_interpreters:
                        if language == "python":
                            self.code_interpreters[language] = PythonInterpreter(
                                preset_functions=pre_load_function_mapping[
                                    os.environ.get("data", ".data/finance.csv")
                                ]
                            )
                        else:
                            self.code_interpreters[language] = CodeInterpreter(
                                language, self.debug_mode
                            )
                    code_interpreter = self.code_interpreters[language]
                    self.last_ran_code = self.messages[-1]["function_call"][
                        "parsed_arguments"
                    ]["code"]
                    output = code_interpreter.run(self.last_ran_code)
                    self.messages.append(
                        {
                            "role": "function",
                            "name": "run_code",
                            "content": output if output else "No output",
                        }
                    )
                    self.respond(
                        plot=plot,
                        show_thinking=show_thinking,
                        store_history=store_history,
                    )
                else:
                    # we're done, check for outputs
                    self.think_step = 0
                    print("We are done")
                    print("last response", self.messages[-1])
                    if store_history:
                        self.chat_history.append(self.messages[-1])
                    if show_thinking:
                        st.markdown(self.messages[-1]["content"])

                    if self.last_ran_code and len(self.last_ran_code) > 0:
                        output_files = get_file_modifications(self.last_ran_code)
                        print("output_files", output_files)
                        if plot:
                            for file in output_files:
                                plot_files(file)
                        # reset if already displayed
                        self.last_ran_code = None
                        self.output_files.extend(output_files)

                    return
