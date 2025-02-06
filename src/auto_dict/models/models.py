from pydantic import BaseModel
from typing import Optional, List

class KeyWord(BaseModel):
    keyword: str

class Keywords(BaseModel):
    keywords: List[KeyWord]


class Defination(BaseModel):
    defination: str
    example: str

class KeywordDefination(BaseModel):
    keyword: str
    defination: Defination

class Dictionary(BaseModel):
    keywords : List[KeywordDefination]



