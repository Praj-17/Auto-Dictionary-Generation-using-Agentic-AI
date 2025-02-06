#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from src.auto_dict.crew import AutoDict

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
from src.auto_dict.utils.split_text import chunk_text
import json
import asyncio

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

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

async def run_long(text):
    """
    Processes a long text by splitting it into chunks, then processing each chunk asynchronously.
    If any result fails during JSON decoding, the corresponding input is reprocessed until successful.
    
    Parameters:
        text (str): The long text to process.
        
    Returns:
        List: A list containing the 'keywords' extracted from each successfully processed chunk.
    """
    # Split the text into chunks
    chunks = chunk_text(text)
    # Create the list of inputs
    inputs = [{"context": context} for context in chunks]
    
    final_keywords = []  # Will accumulate successfully processed keywords
    pending_inputs = inputs
    iteration = 0

    while pending_inputs:
        iteration += 1
        print(f"Iteration {iteration}: Processing {len(pending_inputs)} input(s).")
        try:
            results = await AutoDict().crew().kickoff_for_each_async(inputs=pending_inputs)
        except Exception as e:
            raise Exception(f"An error occurred while running the crew: {e}")

        next_pending_inputs = []
        # Process each result along with its original input
        for input_dict, result in zip(pending_inputs, results):
            ans = result.model_dump()
            try:
                data = json.loads(ans['raw'])
                # Append the successfully decoded keywords
                final_keywords.append(data['keywords'])
            except Exception as e:
                # Collect the input that failed for a retry in the next iteration
                next_pending_inputs.append(input_dict)
        
        if next_pending_inputs:
            print(f"{len(next_pending_inputs)} input(s) failed JSON decoding. Reprocessing them.")
        pending_inputs = next_pending_inputs

    return final_keywords

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
    with open("src/sample_data/paragraphs.txt" , "r") as f:
        text = f.read()
        texts = text.split("\n")
    text= texts[100]

    text = "\n".join(texts[:100])
    output = asyncio.run(run_long(text))

    with open("src/outputs/output_1.json", "w") as f:
        json.dump(output, f, indent=4)

    



