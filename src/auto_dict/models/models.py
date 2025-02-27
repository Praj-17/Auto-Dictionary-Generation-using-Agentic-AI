from pydantic import BaseModel
from enum import Enum
from pydantic import BaseModel
from typing import Optional, List

class POSTags(str, Enum):
    """
    Enumeración de etiquetas de Partes de la Oración (POS).

    Esta clase Enum enumera las etiquetas POS comunes utilizadas en el procesamiento del lenguaje natural.
    Cada etiqueta representa una categoría léxica o función gramatical de una palabra en una oración.
    """
    ADJ = "ADJ"  # Adjetivo
    ADP = "ADP"  # Adposición (preposición, postposición, etc.)
    ADV = "ADV"  # Adverbio
    AUX = "AUX"  # Verbo auxiliar
    CCONJ = "CCONJ"  # Conjunción coordinante
    DET = "DET"  # Determinante
    INTJ = "INTJ"  # Interjección
    NOUN = "NOUN"  # Sustantivo
    NUM = "NUM"  # Numeral
    PART = "PART"  # Partícula
    PRON = "PRON"  # Pronombre
    PROPN = "PROPN"  # Nombre propio
    PUNCT = "PUNCT"  # Puntuación
    SCONJ = "SCONJ"  # Conjunción subordinante
    SYM = "SYM"  # Símbolo
    VERB = "VERB"  # Verbo
    X = "X"  # Otro

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








