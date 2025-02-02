from pydantic import BaseModel, Field
from typing import List, Dict, Any


class SelectModel(BaseModel):
    modelName: str = Field(...)