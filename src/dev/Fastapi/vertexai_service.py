import numpy
import pandas as pd
# import google generative AI API
import google.generativeai as genai   # old version google generative
# from google import genai  # new version google generative


import os, time, json
import uvicorn
import logging
import asyncio
import aiohttp
from dotenv import load_dotenv 

logger= logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

load_dotenv()
PORT = os.environ.get('PORT', default=8000)
logLevel = os.getenv("LOG_LEVEL", default="INFO")
API_KEY = os.getenv("GOOGLE_API_KEY", default="")


# define generation config variables
class CFG(object):
    Temperature = 0.5
    TopP = 0.9
    TopK = 50
    MaxOutputTokens = 100
    ResponseMimeType1 = "text/plain"

generation_config = {    
    "temperature": CFG.Temperature,
    "top_p" : CFG.TopP,
    "top_k" : CFG.TopK, 
     "max_output_tokens" : CFG.MaxOutputTokens,
    # "response_mime_type": CFG.ResponseMimeType1
    
}


class VertexAIService:
    def __init__(self , key= API_KEY):
        # self.data = pd.read_csv("data.csv")
        # initialize google api client
        genai.configure(api_key = key) # for older verion google api client
        # self.client = genai.Client(api_key='GEMINI_API_KEY')
        self.usedModel = ""    
        self.model = None
        self.chatSession = None

    def getCurrentModel(self):
        """
        get current used model
        """
        return self.usedModel
    
    def getChatSession(self, model):
        """
        get the chat session
        """
        return model.start_chat() 


    async def initalizeModel(self, modelName:"models/gemini-2.0-flash-lite-preview" , 
                             config= generation_config, 
                             instruction= None):
        """
        initialize the model
        """
        self.usedModel = modelName
        self.model = genai.GenerativeModel(modelName, generation_config=config , system_instruction=instruction)
        self.chatSession = self.getChatSession(self.model)


    async def getListModels(self):
        """
        get gemini current support models list
        """
        models =  genai.list_models()
        listModels = [ model.name for model in models]
        return listModels
    
    async def generateContext(self, prompt,  config= generation_config):
        """
        generate context based on the prompt
        """
        response = self.model.generate_content(prompt, generation_config=config)
        return response.text
    
    async def chatMode(self, prompt):
        """
        chat mode
        """
        textRes = []
        response = self.chatSession.send_message(prompt, stream=True)
        for chunk in response:
            textRes.append(chunk.text)
        return ''.join(textRes)
