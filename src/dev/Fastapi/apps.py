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
from data_model.vertex_data_model import SelectModel, GenerateContext, ChatModel
from vertexai_service import VertexAIService

from rq import Queue
from redis import Redis
from pydantic import BaseModel
from jobs import *

class JobData(BaseModel):
    lowest : int
    highest : int


logger= logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

load_dotenv()
PORT = os.environ.get('PORT', default=8000)
logLevel = os.getenv("LOG_LEVEL", default="INFO")
API_KEY = os.getenv("GOOGLE_API_KEY", default="")

# set current used model
usedModel = ""
model = None

host = "localhost" #"127.0.0.1"
# start redis connection
redis_conn = Redis(host=host, port=6379)
taskQueue = Queue("task_queue", connection=redis_conn)


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
# genai.configure(api_key = API_KEY)
genaiVertex = VertexAIService()


# inialtize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    return { 
          "success": True,
            "message": "pong"}


# create a job enqueuing the task
@app.post("/job")
async def create_job(jobData: JobData):
    lowest = jobData.lowest
    highest = jobData.highest
    task = taskQueue.enqueue(print_number, lowest, highest) # enqueue
    return {
           "success": True,
          "task_id": task.id}



@app.post("/setModels")
async def set_models(modelName: SelectModel):
    usedModel = modelName.modelName
    modelConfig = None
    if modelName.modelConfig is not None:
        modelConfig = modelName.modelConfig.model_dump()
    # initialize the model
    logger.debug(f"Selected model: {usedModel}")
    logger.debug(f"Model config: {modelConfig}")
    # initialize the model
    if modelConfig is not None:
        await genaiVertex.initalizeModel(usedModel, modelConfig)
    else:
        await genaiVertex.initalizeModel(usedModel)
    return {"models": usedModel}

@app.get("/getmodel")
async def get_model():
    # global usedModel
    currentModel = genaiVertex.getCurrentModel()
    return {"model": currentModel}

@app.post("/generateContext")
async def generateContext( context :GenerateContext):
    # global model
    # prompt = context.prompt
    modelConfig = None
    if context.modelConfig is not None:
        modelConfig = context.modelConfig.model_dump()
    if modelConfig is not None:
        ret = await genaiVertex.generateContext(context.prompt , modelConfig)
    else:
        ret = await genaiVertex.generateContext(context.prompt)
    return {"response": ret}

@app.post("/chat")
async def chat(chat: ChatModel):
    # global model
    prompt = chat.prompt
    # response = chat.response
    ret = await genaiVertex.chatMode(prompt)
    return {"response": ret}
    

@app.get("/getmodel-list")
async def get_model_list():
    listModels = await genaiVertex.getListModels()
    logger.info("List of models: " + str(listModels))
    return {"models": f"{listModels}"}

@app.post("/download-youtube")
async def download_youtube(url: string):
    # download video
    # return {"message": "Video downloaded successfully"}
    # implemenation Message Queued to download video
    pass


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