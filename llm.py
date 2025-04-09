
'''
    Module to interface with LLM hosted via Runpod utilising OpenAI API.
'''

import os

from openai import OpenAI 
from dotenv import load_dotenv

load_dotenv()


def initalise_client():

    '''
        Initialise OpenAI client. 

        Returns:
            * client : (OpenAI): OpenAI client instance.
            * modle_name : (str) : Model of choice. 
    '''

    # Acess environment variables because security. 
    model_name = os.getenv('MODEL_NAME')
    api_key = os.getenv("RUNPOD_API_KEY")
    base_url = os.getenv('RUNPOD_CHATBOT_URL')

    # Initialize the OpenAI Client with your RunPod API Key and Endpoint URL
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    return client, model_name
    

def fetch_chatbot_response(client:object, model_name:str, messages:dict[str:str], temperature:float=0.0, max_tokens:int=500, system_prompt:str='None') -> str:

    '''
        Return generated response from prompt send to LLM through API client

        Paramaters:
            * client : (object) : API client instance to interact with model.
            * model_name : (str) : Model name identifier.
            * messages : (dict[role:str::content:str]) : List of dictionaries encapsulating conversation history.
            * temperature : (float, optional) : Float value to control randomness. 0 as default for deterministic output.
            * max_tokens : (int, options) : Maximum no of tokens for output response. Defaults to 200.
            * system_prompt : (str, Optional) : Extra instructions for the model to follow.
        Returns:
            * str : Chatbot response in string format.
    '''

    if system_prompt:
        # Prepend system prompt for model to follow.
        messages.insert(0, {'role' : 'system', 'content' : system_prompt})

    return client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    ).choices[0].message.content
