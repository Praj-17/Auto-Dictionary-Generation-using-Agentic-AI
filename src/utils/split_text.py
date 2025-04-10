from langchain.text_splitter import CharacterTextSplitter
import string

def count_tokens(text: str) -> int:
    """Counts tokens by splitting the text on whitespace."""
    return len(text)//4

def chunk_text(text: str, chunk_size: int = 4000, chunk_overlap: int = 20):
    """
    Splits the given text into overlapping chunks using LangChain's CharacterTextSplitter.

    Parameters:
        text (str): The input text to split.
        chunk_size (int): The approximate number of tokens per chunk (default is 250).
        chunk_overlap (int): The approximate number of overlapping tokens between chunks (default is 50).

    Returns:
        List[str]: A list of text chunks.
    """
    splitter = CharacterTextSplitter(
        separator=" ",              # Split on whitespace (approximate token boundaries)
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=count_tokens  # Use our custom token counting function
    )
    return splitter.split_text(text)

# Example usage:

def clean_text(text: str) -> str:
    # Ensure UTF-8 encoding and replace errors
    text = text.encode("utf-8", errors="replace").decode("utf-8")
    # Remove punctuation
    return text.translate(str.maketrans('', '', string.punctuation))
if __name__ == '__main__':
    sample_text = (
        "LangChain is a powerful tool for building language model applications. " * 50
    )
    chunks = chunk_text(sample_text, chunk_size=250, chunk_overlap=50)
    
    for i, chunk in enumerate(chunks, start=1):
        print(f"--- Chunk {i} ---")
        print(chunk)
        print()
