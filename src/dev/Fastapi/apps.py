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
model = None


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

def initalizeModel(modelName):
    """
    initialize the model
    """
    model = genai.GenerativeModel(modelName, generation_config=generation_config)
    return model


def getListModels():
    """
    get gemini current support models list
    """
    models = genai.list_models()
    listModels = [ model.name for model in models]
    return listModels

@app.get("/")
async def first_api():
    return {"message": "Hello Johnson"}

@app.post("/setModels")
async def set_models(modelName: SelectModel):
    global usedModel, model
    usedModel = modelName.modelName
    # initialize the model
    model = initalizeModel(usedModel)
    return {"models": usedModel}

@app.get("/getmodel")
async def get_model():
    global usedModel
    return {"model": usedModel}

@app.post("/app/chat")
async def chat(request: Request):
    global model
    response = model.chat(request.json())
    return response

@app.get("/getmodel-list")
async def get_model_list():
    listModels = getListModels()
    logger.info("List of models: " + str(listModels))
    return {"models": f"{listModels}"}

## HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


if __name__ == "__main__":
    uvicorn.run("apps:app", host="0.0.0.0", port=PORT)