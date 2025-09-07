from ollama_apis.run_prompt import chat

CHAR_LIMIT = 5000

def summarize_long_text_recursive(text, prompt, char_limit=CHAR_LIMIT):
    summary = ''
    for i in range(0, len(text), char_limit):
        print(f'Summarize. Processing {i+1} of {len(text)}')
        subtext = text[i:i+char_limit]
        new_summary = chat(prompt + '\n' + subtext)
        summary += '\n' + new_summary
    if len(summary) > char_limit:
        print('Still too long, going again')
        summarize_long_text_recursive(summary, prompt, char_limit=char_limit)
    return summary
