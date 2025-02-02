import os, time, json
import uvicorn

from fastapi import FastAPI,  HTTPException, Request, status
import logging
import asyncio
import aiohttp
from dotenv import load_dotenv 
import google.generativeai as genai
from fastapi.security.api_key import APIKeyHeader 
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from data_model.vertex_data_model import SelectModel


logger= logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

load_dotenv()
PORT = os.environ.get('PORT', default=8000)
logLevel = os.getenv("LOG_LEVEL", default="INFO")
API_KEY = os.getenv("GOOGLE_API_KEY", default="")

# set current used model
usedModel = ""


def set_logging_level(level):
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
    elif level == "CRITICAL":
        logger.setLevel(logging.CRITICAL)
    else:
        logger.setLevel(logging.INFO)

set_logging_level(logLevel)

logger.info("PORT: " + PORT)
# logger.info("Google API Key: " + API_KEY)


# initialize google api client
genai.configure(api_key = API_KEY)

# inialtize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def listModels():
    """
    get gemini current support models list
    """
    models = genai.list_models()
    for model in models:
        logger.info(model.name)
    return models

@app.get("/")
async def first_api():
    return {"message": "Hello Johnson"}

@app.post("setModels")
async def set_models(model: SelectModel):
    usedModel = model
    return {"models": usedModel}

@app.get("/getmodel")
async def get_model():
    return {"model": usedModel}


@app.get("/getmodel-list")
async def get_model_list():
    models = genai.list_models()
    listModels = [ model.name for model in models]
    logger.info("List of models: " + str(listModels))
    return {"models": f"{listModels}"}



if __name__ == "__main__":
    uvicorn.run("apps:app", host="0.0.0.0", port=PORT)