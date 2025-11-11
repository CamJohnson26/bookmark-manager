import os

from dotenv import load_dotenv
from ollama import Client

load_dotenv()

DEFAULT_MODEL = 'gpt-oss:20b'  # Change to your preferred model

client = Client(
  host=os.environ.get("OLLAMA_API_ENDPOINT"),
)

def chat(prompt):
    try:
        response = client.chat(model=DEFAULT_MODEL, messages=[
          {
            'role': 'user',
            'content': prompt,
          },
        ])
        return response['message']['content']
    except Exception as e:
        print('Error during chat:', e)
        raise e

def embed(prompt, model=DEFAULT_MODEL):
    try:
        return client.embed(model=model, input=prompt).embeddings[0]
    except Exception as e:
        print('Error calculating embeddings:', e)
        raise e