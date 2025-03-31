from crewai import Task
from src.agents.agent import keyword_extractor, keyword_researcher, generate_dictionary_agent

keyword_task = Task(
  agent=keyword_extractor,
  description= """ 1. Carefully read the context.
    2. Identify key terms from a student's perspective.
    3. Ensure no redundancy in keywords.
    4. Use concise and precise keywords.
    5. If it is a single word or phrase no need to identify or extract any additional words just pass the word as it is to the researcher. 

    Here is the context: {context}""",
  expected_output=" A structured list of keywords with definitions from the {context}"
)

research_task = Task(
  agent=keyword_researcher,
  description= """  1. Research the extracted keywords online.
    2. Define each keyword with an example.
    3. Determine the correct POS tag.
    4. Avoid redundancy.
    5. Keep keywords in the original language.
    6.  if input is a single word or phrase research only about its defination etc no other words
    POS Tag should be one of these

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
    X = "X"  # Otro""",
  expected_output="  A structured list of keywords with definitions."
)

generate_dictionary_task = Task(
  agent=generate_dictionary_agent,
  description= """      1. Review the keywords and definitions.
    2. Create a structured dictionary.
    3. Ensure clarity and original language.""",
  expected_output="""
    A comprehensive dictionary with keywords and definitions and other metadata in a markdown format.
    Return only the following format do not return outputs from other agents only use them as reference
    Number Each keyword and definition pair in a numbered list
    separate all metadata with new lines
    
    **Keyword**: keyword
    **Definition**: definition
    **Pos**: POS tag name
    **Example**: example

    POS Tag should be one of these

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
"""
)
