from pydantic import BaseModel, field_validator
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


from pydantic import ValidationError

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
    test_dictionary_entry()

