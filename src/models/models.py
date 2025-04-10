from pydantic import BaseModel, field_validator
from enum import Enum
from typing import List, Optional
import json

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
    UNKNOWN = "UNKNOWN"

class DictionaryEntry(BaseModel):
    word: str
    definition: str
    pos: Optional[POSTags] = None

    @field_validator("pos", mode="before")
    def validate_pos(cls, value):
        if value is None:
            return value
        try:
            return POSTags(value)
        except ValueError:
            return POSTags.UNKNOWN

class Dictionary(BaseModel):
    entries: List[DictionaryEntry]

def test_dictionary_entry():
    # Valid POS Tag
    entry1 = DictionaryEntry(word="run", definition="Move at a speed faster than a walk", pos="VERB")
    assert entry1.pos == POSTags.VERB
    print(f"Test 1 Passed: {entry1.pos}")

    # Invalid POS Tag (should be set to UNKNOWN)
    entry2 = DictionaryEntry(word="quickly", definition="At a fast speed", pos="INVALID_TAG")
    assert entry2.pos == POSTags.UNKNOWN
    print(f"Test 2 Passed: {entry2.pos}")

    # No POS Tag Provided (should remain None)
    entry3 = DictionaryEntry(word="happy", definition="Feeling or showing pleasure")
    assert entry3.pos is None
    print(f"Test 3 Passed: {entry3.pos}")

    # Creating a dictionary with multiple entries
    dictionary = Dictionary(entries=[entry1, entry2, entry3])
    assert len(dictionary.entries) == 3
    print("Test 4 Passed: Dictionary created successfully with 3 entries")

if __name__ == "__main__":
    # test_dictionary_entry()
   output =  Dictionary.model_validate_json("""```json
    {
    "entries": [
        {
        "word": "Aves",
        "definition": "Grupo diverso de animales vertebrados caracterizados por su capacidad para volar, con plumas, alas y pico.",
        "pos": "NOUN"
        },
        {
        "word": "Animales vertebrados",
        "definition": "Grupo de animales con esqueleto cartilaginoso o óseo, pertenecientes a filos como Aves, Mamíferos, etc.",
        "pos": "NOUN"
        },
        {
        "word": "Plumas",
        "definition": "Estructuras biológicas que cubren la piel de las aves, proporcionándoles protección y ayudando en su termorregulación.",
        "pos": "NOUN"
        },
        {
        "word": "Alas",
        "definition": "Órganos adaptados para el vuelo, formados por una serie de plumas unidas y controladas muscularmente.",
        "pos": "NOUN"
        },
        {
        "word": "Pico",
        "definition": "Parte del esqueleto y herramienta anatómica con la que las aves se alimentan.",
        "pos": "NOUN"
        },
        {
        "word": "Volar",
        "definition": "Capacidad que poseen la mayoría de las aves, aunque hay especies como el pingüino o el avestruz que no pueden volar.",
        "pos": "VERB"
        },
        {
        "word": "Hábitats naturales",
        "definition": "Ambientes que proporcionan el entorno necesario para la vida de las comunidades de plantas y animales.",
        "pos": "NOUN"
        },
        {
        "word": "Ecosistemas",
        "definition": "Comunidades de organismos interdependientes que interactúan con su entorno, incluyendo la polinización y el control de insectos por parte de ciertas aves.",
        "pos": "NOUN"
        },
        {
        "word": "Dispersión de semillas",
        "definition": "Proceso clave en la biodiversidad y la regeneración de hábitats naturales, facilitado por algunas aves.",
        "pos": "NOUN"
        },
        {
        "word": "Canto",
        "definition": "Comportamiento comunicativo y expresivo de muchas aves que puede ser musical y apreciado por personas.",
        "pos": "NOUN"
        },
        {
        "word": "Colorido plumaje",
        "definition": "Característica distintiva de las aves que atrae a los humanos por su belleza y diversidad.",
        "pos": "NOUN"
        },
        {
        "word": "Fascinantes para muchas personas",
        "definition": "Las aves son objeto de gran interés y atracción debido a su belleza y comportamiento.",
        "pos": "ADJ"
        }
    ]
    }
    ```""")
   
   print(output)

