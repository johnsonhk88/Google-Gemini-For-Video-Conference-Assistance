from pydantic import BaseModel, Field
from typing import List, Dict, Any


## Define API Parameters model 

class SelectModel(BaseModel):
    modelName: str = Field(... , description="Model name")


class GenerateContext(BaseModel):
    prompt: str = Field(... , description="Prompt for generating context")


