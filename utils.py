#load environment variables from the .env file
import os
from os.path import join, dirname
import os
import shutil
import tempfile
from typing import Optional

import streamlit as st  # type: ignore

from codeinterpreterapi import CodeInterpreterSession

def load_dotenv():
    dotenv_path = join(dirname(__file__), '.env')
    # read each line and assign env var name and value split by '='
    print("loading env file from: ", dotenv_path)
    for line in open(dotenv_path):
        var = line.strip().split('=')
        if len(var) == 2:
            key, value = var[0].strip(), var[1].strip()
            # set the env var
            os.environ[key] = value




def create_temp_folder() -> str:
    """
    Creates a temp folder
    """
    temp_folder = tempfile.mkdtemp()
    return temp_folder


async def get_images(prompt: str, files: Optional[list] = None):
    if files is None:
        files = []
    with st.spinner():
        async with CodeInterpreterSession(model="gpt-4") as session:
            response = await session.generate_response(prompt, files=files)

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
                else:
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
