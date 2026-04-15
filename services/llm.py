import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")


def call_llm(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/elephant-alpha",  # ✅ your model
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )   

        data = response.json()

        print("LLM RAW RESPONSE:", data)

        # ✅ handle errors cleanly
        if "error" in data:
            return f"LLM Error: {data['error']['message']}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM ERROR:", e)
        return "LLM failed"