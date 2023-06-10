from transformers import pipeline


def get_summary(text):
    print("Loading NLP tools...")
    summarization = pipeline("summarization")

    # https://www.thepythoncode.com/article/text-summarization-using-huggingface-transformers-python
    if len(text) >= 1024:
        text = text[:1024]
    summary = summarization(text, )[0]['summary_text']
    return summary
