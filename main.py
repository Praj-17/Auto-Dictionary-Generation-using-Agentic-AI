#!/usr/bin/env python
import sys
import warnings

from datetime import datetime
from src.auto_dict.utils.to_pydantic import TextToPydanticConverter

from src.auto_dict.crew import AutoDict
from src.auto_dict.utils.split_text import clean_text
from src.auto_dict.models.models import Dictionary

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from src.auto_dict.utils.split_text import chunk_text
import json
import asyncio

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

to_pydantic = TextToPydanticConverter()

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }
    
    try:
        AutoDict().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

async def run_long(text, max_retries=5):
    """
    Processes a long text by splitting it into chunks and processing each chunk asynchronously.
    Each chunk is retried (up to max_retries) if processing fails.
    
    Parameters:
        text (str): The long text to process.
        max_retries (int): Maximum number of retries per chunk.
        
    Returns:
        str: A markdown string containing the aggregated markdown strings from each successfully processed chunk.
    """
    # Split the text into chunks and initialize each input with a retry count
    chunks = chunk_text(text)
    inputs = [{"context": chunk, "retry_count": 5} for chunk in chunks]
    
    final_markdown = []  # Accumulates raw markdown strings from each successful processing
    pending_inputs = inputs
    iteration = 0
    converted_json = []

    while pending_inputs:
        iteration += 1
        print(f"Iteration {iteration}: Processing {len(pending_inputs)} input(s).")
        
        try:
            # Assume each result is a JSON dict with a "raw" key containing a markdown string
            results = await AutoDict().crew().kickoff_for_each_async(inputs=pending_inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

        next_pending_inputs = []
        # Process each result with its corresponding input
        for input_dict, result in zip(pending_inputs, results):
            try:
                print(f"Result: {result.model_dump()['raw']}")
                # Append the raw markdown string from the "raw" key in the JSON dict
                final_markdown.append(result.model_dump()['raw'])
            except Exception as e:
                # Increment retry count and add back if below max_retries
                input_dict["retry_count"] += 1
                if input_dict["retry_count"] < max_retries:
                    next_pending_inputs.append(input_dict)
                else:
                    print(f"Max retries reached for input with context: {input_dict['context'][:30]}...")
        
        if next_pending_inputs:
            print(f"{len(next_pending_inputs)} input(s) failed processing. Reprocessing them.")
        pending_inputs = next_pending_inputs

        try:
            # convert to json 
            converted_json = to_pydantic.convert(text_sample="\n".join(final_markdown), model_class=Dictionary)
            print("Converted to json")
        except Exception as e:
            raise Exception(f"An error occurred while converting to json: {e}")


    return converted_json

def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        AutoDict().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AutoDict().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "context": "A GUI may be designed for the requirements of a vertical market as application-specific graphical user interfaces. Examples include automated teller machines (ATM), point of sale (POS) touchscreens at restaurants, self-service checkouts used in a retail store, airline self-ticket and check-in, information kiosks in a public space, like a train station or a museum, and monitors or control screens in an embedded industrial application which employ a real-time operating system (RTOS)."
    }
    try:
        AutoDict().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == '__main__':
    # with open("src/sample_data/paragraphs.txt" , "r") as f:
    #     text = f.read()
    #     texts = text.split("\n")
   


    # text = "\n".join(texts[:150])

    text = """Artículo de investigación


RESUMEN

Introducción: El Perú es uno de los países con mayor biodiversidad en especies botánicas, algunas con propiedades medicinales conocidas.
Objetivo: Determinar el efecto antibacteriano del aceite esencial de las hojas de Eugenia stipitata McVaugh frente a Staphylococcus aureus ATCC 25923, Escherichia coli ATCC 25922 y Salmonella enterica sv Enteritidis ATCC 13076.
Métodos: Estudio de tipo básico con enfoque cuantitativo y experimental. Las plantas provienen del distrito de Belén, ciudad de Iquitos, Departamento de Loreto. La técnica para la extracción del aceite esencial fue la de arrastre de vapor y la técnica microbiológica para determinar el efecto antimicrobiano la de Kirby Bauer. Se trabajaron las muestras en 4 concentraciones 100, 75, 50 y un 25 %; un control negativo solo con dimetilsulfóxido, se utilizaron 5 repeticiones por cada muestra.
Resultados: La muestra a concentración al 100 % tuvo actividad antibacteriana contra Staphylococcus aureus. La actividad del ensayo frente a Escherichia coli demostró ser efectiva en todas las muestras, sin embargo, se observó que los halos de inhibición de mayor diámetro se manifestaron en las muestras al 100 % y 75 %. Además, se evidenció actividad antibacteriana a concentraciones del 100 %, 75 % y un 50 % frente a Salmonella enterica sv Enteritidis.
Conclusiones: El aceite esencial de las hojas de Eugenia stipitata McVaugh presenta efecto antibacteriano frente a Staphylococcus aureus, Escherichia coli y Salmonella enterica sv Enteritidis.

Palabras clave: aceites volátiles; antibacterianos; Escherichia coli; Salmonella entérica; Staphylococcus aureus.

ABSTRACT
."""

    output = asyncio.run(run_long(clean_text(text)))
    print(output)
    
    if isinstance(output, dict):
        with open("src/outputs/output_spanish.json", "w") as f:
            json.dump(output, f, indent=4)
    elif isinstance(output, str):
        with open("src/outputs/output_spanish.md", "w") as f:
            f.write(f"# Keywords Extracted\n \n {output}")




    



