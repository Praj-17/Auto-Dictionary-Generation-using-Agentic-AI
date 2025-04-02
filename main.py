from dotenv import load_dotenv
import json
import asyncio
from src.utils.split_text import chunk_text, clean_text
from src.utils.to_pydantic import TextToPydanticConverter
from src.crew import auto_dict_crew
from src.models.models import Dictionary
from database import save_word  # ✅ Import MongoDB function to save words

# ✅ Load environment variables
load_dotenv()

to_pydantic = TextToPydanticConverter()

async def run_long(text, max_retries=5):
    """
    Processes a long text by splitting it into chunks and processing each chunk asynchronously.
    Each chunk is retried (up to max_retries) if processing fails.
    
    Parameters:
        text (str): The long text to process.
        max_retries (int): Maximum number of retries per chunk.
        
    Returns:
        list: A list of dictionaries, each containing a word and its definition.
    """
    chunks = chunk_text(text)
    inputs = [{"context": chunk, "retry_count": 5} for chunk in chunks]
    
    final_markdown = []  
    pending_inputs = inputs
    iteration = 0

    while pending_inputs:
        iteration += 1
        print(f"Iteration {iteration}: Processing {len(pending_inputs)} input(s).")
        
        try:
            results = await auto_dict_crew.kickoff_for_each_async(inputs=pending_inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

        next_pending_inputs = []
        for input_dict, result in zip(pending_inputs, results):
            try:
                print(f"Result: {result.model_dump()['raw']}")
                final_markdown.append(result.model_dump()['raw'])
            except Exception as e:
                input_dict["retry_count"] += 1
                if input_dict["retry_count"] < max_retries:
                    next_pending_inputs.append(input_dict)
                else:
                    print(f"Max retries reached for input with context: {input_dict['context'][:30]}...")

        if next_pending_inputs:
            print(f"{len(next_pending_inputs)} input(s) failed processing. Reprocessing them.")
        pending_inputs = next_pending_inputs

    try:
        # ✅ Ensure the JSON structure is valid before accessing 'meaning'
        converted_json = to_pydantic.convert(text_sample=text, model_class=Dictionary)
        
        print("✅ Full JSON Response:")
        print(json.dumps(converted_json, indent=4))  # ✅ Print the full JSON for debugging
        
        if isinstance(converted_json, dict):
            if "entries" in converted_json:
                words_list = converted_json["entries"]  # ✅ Extract from 'entries' instead of 'meaning'
            elif "meaning" in converted_json:
                words_list = converted_json["meaning"]  # ✅ Fallback if 'meaning' exists
            else:
                print("❌ Error: JSON does not contain 'entries' or 'meaning'")
                return {"error": "Invalid JSON structure, missing 'entries' or 'meaning'"}

            if isinstance(words_list, list):
                # ✅ Save each word separately instead of storing them as a list
                for word_entry in words_list:
                    if isinstance(word_entry, dict) and "word" in word_entry and "definition" in word_entry:
                        word_data = {
                            "word": word_entry["word"],
                            "definition": word_entry["definition"]
                        }
                        save_word(word_data)  # ✅ Save each word independently
                        print(f"✅ Saved: {word_data}")
                    else:
                        print("⚠️ Skipping invalid word entry:", word_entry)

                return words_list
            else:
                print("❌ Error: 'entries' or 'meaning' field is not a list")
                return {"error": "'entries' or 'meaning' field is not a list"}
        else:
            print("❌ Error: Invalid JSON structure, expected dictionary")
            return {"error": "Invalid JSON structure, expected dictionary"}
    except Exception as e:
        print(f"❌ Error in run_long(): {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    text = """Artículo de investigación

    RESUMEN

    Introducción: El Perú es uno de los países con mayor biodiversidad en especies botánicas, algunas con propiedades medicinales conocidas.
    Objetivo: Determinar el efecto antibacteriano del aceite esencial de las hojas de Eugenia stipitata McVaugh frente a Staphylococcus aureus ATCC 25923, Escherichia coli ATCC 25922 y Salmonella enterica sv Enteritidis ATCC 13076.
    Métodos: Estudio de tipo básico con enfoque cuantitativo y experimental. Las plantas provienen del distrito de Belén, ciudad de Iquitos, Departamento de Loreto. La técnica para la extracción del aceite esencial fue la de arrastre de vapor y la técnica microbiológica para determinar el efecto antimicrobiano la de Kirby Bauer. Se trabajaron las muestras en 4 concentraciones 100, 75, 50 y un 25 %; un control negativo solo con dimetilsulfóxido, se utilizaron 5 repeticiones por cada muestra.
    Resultados: La muestra a concentración al 100 % tuvo actividad antibacteriana contra Staphylococcus aureus. La actividad del ensayo frente a Escherichia coli demostró ser efectiva en todas las muestras, sin embargo, se observó que los halos de inhibición de mayor diámetro se manifestaron en las muestras al 100 % y 75 %. Además, se evidenció actividad antibacteriana a concentraciones del 100 %, 75 % y un 50 % frente a Salmonella enterica sv Enteritidis.
    Conclusiones: El aceite esencial de las hojas de Eugenia stipitata McVaugh presenta efecto antibacteriano frente a Staphylococcus aureus, Escherichia coli y Salmonella enterica sv Enteritidis.

    Palabras clave: aceites volátiles; antibacterianos; Escherichia coli; Salmonella entérica; Staphylococcus aureus.

    ABSTRACT
    """

    output = asyncio.run(run_long(clean_text(text)))

    if isinstance(output, list):
        with open("outputs/output_spanish_3.json", "w") as f:
            json.dump(output, f, indent=4)
        print("✅ Output successfully saved to JSON.")
    else:
        print("⚠️ Output is not valid JSON:", output)
