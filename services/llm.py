import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_llm(prompt):
    for attempt in range(3):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    # ✅ WORKING MODELS (pick one)
                    "model": "openai/gpt-3.5-turbo",
                    # alternatives:
                    # "model": "meta-llama/llama-3-8b-instruct",
                    # "model": "google/gemma-7b-it",

                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )

            data = response.json()

            print("LLM RAW RESPONSE:", data)

            if "error" in data:
                print("Retrying...", attempt + 1)
                continue

            return data["choices"][0]["message"]["content"]

        except Exception as e:
            print("LLM ERROR:", e)

    return "LLM failed after retries"