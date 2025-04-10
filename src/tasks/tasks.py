from crewai import Task
from src.agents.agent import keyword_extractor, keyword_researcher, generate_dictionary_agent
from src.models.models import Dictionary

keyword_task = Task(
  agent=keyword_extractor,
  description= """ 1. Carefully read the context.
    2. Identify key terms from a student's perspective.
    3. Ensure no redundancy in keywords.
    4. Use concise and precise keywords.
    5. If it is a single word or phrase, do not identify or extract any additional words; just pass the word as it is to the researcher. 

    Here is the context: {context}""",
  expected_output=" A structured list of keywords with definitions from the {context} in {language}."
)

research_task = Task(
  agent=keyword_researcher,
  description= """  1. Research the extracted keywords online.
    2. Define each keyword with an example.
    3. Determine the correct POS tag.
    4. Avoid redundancy.
    5. Keep keywords in the original language.
    6. If the input is a single word or phrase, research only its definition, etc., without adding other words.
    7. Strictly do not research any new or related words, only find definations for the given keywords.
    
    POS Tag should be one of these:

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
    X = "X"  # Other""",
  expected_output=" A structured list of keywords with definitions in {language}."
)

generate_dictionary_task = Task(
  agent=generate_dictionary_agent,
  description= """      1. Review the keywords and definitions.
    2. Create a structured dictionary.
    3. Ensure clarity and maintain the original language.""",
  expected_output="""
    A comprehensive dictionary with keywords, definitions,in {langauge} and other metadata in a markdown format.
    Do not return outputs from other agents, only use them as references.
    Number each keyword and definition pair in a numbered list.
    Separate all metadata with new lines.
    Return a list of dictentionary entries in a JSON format.
    Each entry should have the following fields:
    - word: The keyword.
    - definition: The definition of the keyword.
    - pos: The part of speech (POS) tag. (optional)
    
    POS Tag should be one of these:

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
""", 
output_pydantic=Dictionary
)
