import openai

def chat_with_openai(api_key: str, prompt: str) -> str:
    openai.api_key = api_key
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"[OpenAI Error] {e}"
