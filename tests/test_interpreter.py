from luana_engine.utils import load_dotenv
from luana_engine import interpreter

load_dotenv()


def test_chat():
    agent = interpreter.Interpreter()
    result = agent.chat("Hi", True)
    print(result)


test_chat()
