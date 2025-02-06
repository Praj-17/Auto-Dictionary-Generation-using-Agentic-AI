from pydantic import BaseModel
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class POSTags(str, Enum):
    """
    Enumeration of Part-of-Speech (POS) tags.

    This Enum class lists common POS tags used in natural language processing.
    Each tag represents a lexical category or grammatical function of a word in a sentence.
    """
    ADJ = "ADJ"  # Adjective
    ADP = "ADP"  # Adposition (preposition, postposition, etc.)
    ADV = "ADV"  # Adverb
    AUX = "AUX"  # Auxiliary verb
    CCONJ = "CCONJ"  # Coordinating conjunction
    DET = "DET"  # Determiner
    INTJ = "INTJ"  # Interjection
    NOUN = "NOUN"  # Noun
    NUM = "NUM"  # Numeral
    PART = "PART"  # Particle
    PRON = "PRON"  # Pronoun
    PROPN = "PROPN"  # Proper noun
    PUNCT = "PUNCT"  # Punctuation
    SCONJ = "SCONJ"  # Subordinating conjunction
    SYM = "SYM"  # Symbol
    VERB = "VERB"  # Verb
    X = "X"  # Other

class KeyWord(BaseModel):
    keyword: str

class Keywords(BaseModel):
    keywords: List[KeyWord]


class Defination(BaseModel):
    defination: str
    example: str
    pos_tag: POSTags
    alternate_meaning: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None


class KeywordDefination(BaseModel):
    keyword: str
    defination: Defination

class Dictionary(BaseModel):
    keywords : List[KeywordDefination]








