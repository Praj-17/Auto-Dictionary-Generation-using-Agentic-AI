from langdetect import detect_langs
import pycountry

# Function to get the full language name
def get_language_name(lang_code):
    try:
        language = pycountry.languages.get(alpha_2=lang_code)
        return language.name
    except AttributeError:
        return lang_code  # If the language code is not found, return the code itself

# Function to detect the language and return its full name
def detect_language_full_name(text):
    # Detect languages and their probabilities
    languages = detect_langs(text)

    # Sort by highest probability and get the top language
    top_language = max(languages, key=lambda x: x.prob)

    # Get the full language name
    language_full_name = get_language_name(top_language.lang)
    
    return language_full_name

if __name__ == "__main__":
# Example usage
    text = "Hola, ¿cómo estás?"
    language = detect_language_full_name(text)
    print(f"The language detected is: {language}")
