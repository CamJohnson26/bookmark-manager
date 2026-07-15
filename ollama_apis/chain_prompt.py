from ollama_apis.run_prompt import chat

CHAR_LIMIT = 5000

def summarize_long_text_recursive(text, prompt, char_limit=CHAR_LIMIT, max_rounds=3):
    if not text or not text.strip():
        raise ValueError('Cannot summarize empty text')

    summary = ''
    for i in range(0, len(text), char_limit):
        print(f'Summarize. Processing {i+1} of {len(text)}')
        subtext = text[i:i+char_limit]
        new_summary = chat(prompt + '\n' + subtext)
        if not new_summary or not new_summary.strip():
            raise ValueError('Summarization returned empty output')
        summary += '\n' + new_summary
    summary = summary.strip()
    if len(summary) > char_limit and max_rounds > 0:
        print('Still too long, going again')
        return summarize_long_text_recursive(
            summary,
            prompt,
            char_limit=char_limit,
            max_rounds=max_rounds - 1,
        )
    return summary
