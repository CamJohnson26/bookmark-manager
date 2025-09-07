from ollama_apis.run_prompt import chat
from ollama_apis.prompts import SUMMARIZATION_PROMPT


def get_summary(text):
    print("Loading NLP tools...")

    # Format the prompt with the text
    prompt = SUMMARIZATION_PROMPT.format(text=text)

    # Get summary from Ollama
    summary = chat(prompt)
    return summary
