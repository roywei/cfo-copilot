#load environment variables from the .env file
import os
from os.path import join, dirname


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