from ollama_apis.run_prompt import chat
from ollama_apis.prompts import SUMMARIZATION_PROMPT


def get_summary(text):
    if not text or not text.strip():
        raise ValueError("Cannot summarize empty page text")

    print("Loading NLP tools...")

    # Format the prompt with the text
    prompt = SUMMARIZATION_PROMPT.format(text=text)

    # Get summary from Ollama
    summary = chat(prompt)
    if not summary or not summary.strip():
        raise ValueError("Summarization returned empty output")

    return summary.strip()
