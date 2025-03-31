from dotenv import load_dotenv
import json
from src.utils.split_text import chunk_text, clean_text
from src.utils.to_pydantic import TextToPydanticConverter
from src.crew import auto_dict_crew
from src.models.models import Dictionary
from src.database import save_word  # ✅ Import MongoDB function to save words
import asyncio

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
        dict: A JSON-compatible dictionary containing extracted words.
    """
    chunks = chunk_text(text)
    inputs = [{"context": chunk, "retry_count": 5} for chunk in chunks]
    
    final_markdown = []  
    pending_inputs = inputs
    iteration = 0
    converted_json = {}  # ✅ Store as a dictionary, not a list

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
            # convert to json 
            converted_json = to_pydantic.convert(text_sample="\n".join(final_markdown), model_class=Dictionary)
        except Exception as e:
            raise Exception(f"An error occurred while converting to json: {e}")


    return converted_json

async def run_short(word):
    """
    Processes a single word or phrase to get its meaning.

    Parameters:
        word (str): The word or phrase to process.

    Returns:
        dict: A dictionary containing the processed result.
    """
    converted_json = {}
    try:
        # Clean the input word or phrase
        cleaned_word = clean_text(word)
        
        # Process the input using the auto_dict_crew
        result = auto_dict_crew.kickoff(inputs={"context": cleaned_word})

        print(result, type(result))
        
        # Convert the result to the desired JSON format
        try:
            converted_json = to_pydantic.convert(text_sample=str(result), model_class=Dictionary)
        except Exception as e:
            raise Exception(f"An error occurred while converting to json: {e}")

        return converted_json
    except Exception as e:
        raise Exception(f"An error occurred while processing the word: {e}")
if __name__ == "__main__":
  text = """Oncology"""

  output = asyncio.run(run_short(clean_text(text)))
  print("output")
  print(output)


  if isinstance(output, dict):
      with open("outputs/output_spanish_3.json", "w") as f:
          json.dump(output, f, indent=4)
      # with open("output_spanish_3.md", "w") as f:
      #     f.write(f"# Keywords Extracted\n \n {output['raw']}")
