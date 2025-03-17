from pydantic import BaseModel
from enum import Enum
from typing import List, Optional

class POSTags(str, Enum):
    ADJ = "ADJ"
    ADP = "ADP"
    ADV = "ADV"
    AUX = "AUX"
    CCONJ = "CCONJ"
    DET = "DET"
    INTJ = "INTJ"
    NOUN = "NOUN"
    NUM = "NUM"
    PART = "PART"
    PRON = "PRON"
    PROPN = "PROPN"
    PUNCT = "PUNCT"
    SCONJ = "SCONJ"
    SYM = "SYM"
    VERB = "VERB"
    X = "X"

class DictionaryEntry(BaseModel):
    word: str
    definition: str
    pos: Optional[POSTags] = None

class Dictionary(BaseModel):
    entries: List[DictionaryEntry]
