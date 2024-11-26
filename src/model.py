from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Answer(BaseModel):
    user_id:   Annotated[int, Field(strict=True, gt=0)]
    text_id:   Annotated[int, Field(strict=True, gt=0)] 
    interest:  Annotated[int, Field(strict=True, ge=0, le=7)] 
    difficult: Annotated[int, Field(strict=True, ge=0, le=7)] 


class Text(BaseModel):
    id:   Annotated[int, Field(strict=True, gt=0)]
    text:      str
    topic:     str 
    difficult: str


class TextWrite(BaseModel):
    text:      str
    topic:     str 
    difficult: str