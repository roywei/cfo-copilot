import openai
import os
from utils import load_dotenv
from langchain.agents import create_pandas_dataframe_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI
import pandas as pd
from modules.config import CHAT_MODEL, COMPLETIONS_MODEL

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

# A basic class to create a message as a dict for chat
class Message:
    
    def __init__(self, role, content):
        self.role = role
        self.content = content
        
    def message(self):
        return {
            "role": self.role,
            "content": self.content
        }

class Assistant:
    
    def __init__(self):
        self.conversation_history = []
        self.data = None
        self.agent = None
       

    def provide_data(self, data):
        self.data = data
        self.agent = create_pandas_dataframe_agent(
                ChatOpenAI(temperature=0, model="gpt-4"),
                data,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
        )

    def _get_assistant_response(self, prompt):
        try:
            """
            completion = openai.ChatCompletion.create(
              model=CHAT_MODEL,
              messages=prompt,
              temperature=0.1
            )
            
            # Return the message content directly without creating a Message object
            response_content = completion['choices'][0]['message']['content']
            response_role = completion['choices'][0]['message']['role']
            
            return {
                "role": response_role,
                "content": response_content
            }
            """
            return {"role": "Assistant", "content" : self.agent.run(prompt)}
        except Exception as e:
            return f'Request failed with exception {e}'
    
    def ask_assistant(self, next_user_prompt):
        # Since next_user_prompt is a list, access the first element to get the Message object
        # and then call the message() method
        self.conversation_history.append(next_user_prompt[0].message())
        assistant_response = self._get_assistant_response(self.conversation_history)
        print("response is ", assistant_response)
        return assistant_response
        
            
    def pretty_print_conversation_history(
            self, 
            colorize_assistant_replies=True):
        
        for entry in self.conversation_history:
            if entry['role']=='system':
                pass
            else:
                prefix = entry['role']
                content = entry['content']
                if colorize_assistant_replies and entry['role'] == 'assistant':
                    output = colored(f"{prefix}:\n{content}, green")
                else:
                    output = colored(f"{prefix}:\n{content}")
                print(output)