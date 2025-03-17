# Auto-Dictionary Generation using Agentic-AI

## Overview

The "Auto-Dictionary Generation using Agentic-AI" project is an innovative approach to automatically creating dictionaries using agentic AI. This project leverages the capabilities of AI agents to define words, provide example sentences, and generate comprehensive dictionary entries, streamlining the dictionary creation process.

## Features

-   **Automated Word Definition:** Utilizes AI agents to generate accurate and context-aware definitions for words.
-   **Example Sentence Generation:** Provides example sentences to illustrate the usage of words in different contexts.
-   **Comprehensive Dictionary Entries:** Combines definitions and examples to create detailed dictionary entries.
-   **Efficient Dictionary Creation:** Automates the dictionary creation process, saving time and resources.
-   **Extensible Architecture:** Designed with an extensible architecture to incorporate new words, definitions, and functionalities.

## Installation

To set up the project locally, follow these steps:

1.  Clone the repository:

    ```
    git clone https://github.com/Praj-17/Auto-Dictionary-Generation-using-Agentic-AI.git
    cd Auto-Dictionary-Generation-using-Agentic-AI
    ```

2.  Install the required dependencies. It is recommended to use a virtual environment:

    ```
    Install python ==3.10.x
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```
3. Install Ollama

- Install the Ollama Package on your system from this website [OLLAMA download](https://ollama.com/download/windows)

4. Pull the `llama3.2` model

```
ollama pull llama3.2
```

## Usage

1.  **Configuration:**

    -   Configure the necessary API keys and environment variables in the `.env` file.
    -   Modify the `src/auto_dict/configs` file to adjust any specific settings.
    - You only need to add the [Serper-API-KEY](https://serper.dev/) Generate it from this [link](https://serper.dev/)

    - Paste the key in the `.env` file

2.  **Running the Project:**

    -   To start the automated dictionary generation, run the main script:

        ```
        python main.py
        ```

3.  **Reviewing the Output:**

    -   The generated dictionary entries will be saved in the designated output file.
    -   Review and validate the entries for accuracy and completeness.

## Architecture

The project architecture consists of the following key components:

-   **AI Agent Module:** Responsible for generating word definitions and example sentences.
-   **Data Processing Module:** Handles data input, processing, and output.
-   **Dictionary Generation Module:** Combines the generated definitions and examples to create dictionary entries.
-   **API Integration Module:** Connects with external APIs for enhanced functionality.

## Contributing

Contributions are welcome! Here are some ways you can contribute:

-   **Report Issues:** Submit bug reports and feature requests through GitHub issues.
-   **Submit Pull Requests:** Contribute code improvements, new features, and bug fixes.
-   **Improve Documentation:** Help enhance the project documentation.

Please follow these guidelines when contributing:

-   Follow the established coding style.
-   Write clear and concise commit messages.
-   Test your changes thoroughly.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions, issues, or contributions, please contact [Praj-17](https://github.com/Praj-17).


