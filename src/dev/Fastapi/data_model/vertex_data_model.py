from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


## Define API Parameters model 


class GenerationConfig(BaseModel):
    temperature: float = Field(0.4, description="temperature parameter for text generation")
    top_p: float = Field(0.9, description="top-p parameter for text generation")
    top_k: int = Field(32, description="top-k parameter for text generation")
    max_output_tokens: int = Field(2048, description="maximum number of tokens to generate")

class SelectModel(BaseModel):
    modelName : str = Field(default="gemini-2.0-flash-001" , description="Model name" , example="models/gemini-2.0-flash-lite-preview")
    instructions : Optional[List[str]] = Field(default=None, description="Instruction for model", example=["You are a Video Assistance.","Your mission is Summary and Extraction the Video"])
    modelConfig : Optional[GenerationConfig] = Field(default=None, description="Model configuration")


class GenerateContext(BaseModel):
    prompt: str = Field(default=None , description="Prompt for generating context", example="What is LLM model?")
    modelConfig : Optional[GenerationConfig] = Field(default=None, description="Model configuration")


class ChatModel(BaseModel):
    prompt: str = Field(default=None , description="Prompt for generating context", example="What is LLM model?")
    # modelConfig : Optional[GenerationConfig] = Field(default=None, description="Model configuration")
    # response: Optional[str] = Field(default=None, description="Response from model")