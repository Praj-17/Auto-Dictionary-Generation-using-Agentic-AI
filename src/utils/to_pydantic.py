from pydantic import BaseModel
import json
from SimplerLLM.language.llm import LLM, LLMProvider
from SimplerLLM.language.llm_addons import generate_pydantic_json_model


# Define a sample Pydantic model
class LLMResponse(BaseModel):
    response: str

# Create an LLM instance using Ollama as the provider with the model "llama3.2:latest"


# Class that converts a given text sample into a Pydantic model instance
class TextToPydanticConverter:
    def __init__(self,):
        self.llm_instance = LLM.create(provider=LLMProvider.OLLAMA, model_name="llama3.2:latest")
    
    def build_conversion_prompt(self, text_sample:str) -> str:
        return f"""You are tasked with converting the given text sample into a given pydantic model.
          The text sample is: {text_sample} Make sure to follow the same language,  style and structure as the given text sample."""

    def convert(self, text_sample: str, model_class: BaseModel) -> BaseModel:
        """
        Converts the text sample to an instance of the provided Pydantic model.

        Parameters:
            text_sample (str): The text prompt to be processed.
            model_class (BaseModel): The Pydantic model class to generate.

        Returns:
            BaseModel: An instance of the provided Pydantic model with the generated data.
        """
        output_model = generate_pydantic_json_model(
            llm_instance=self.llm_instance,
            prompt=text_sample,
            model_class=model_class
        )

        if isinstance(output_model, model_class):
            return output_model.model_dump()
        elif isinstance(output_model, str) and "[" in output_model:
            return model_class.model_validate_json(output_model)
        elif isinstance(output_model, dict):
            return output_model      
        return output_model

# Example usage:
if __name__ == "__main__":
    converter = TextToPydanticConverter()
    text_sample = "generate a sentence about the importance of AI"
    result_model = converter.convert(text_sample, LLMResponse)
    print(result_model.model_dump())
