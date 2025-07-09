import openai

async def call_chatgpt(user_message: str, api_key: str, model: str = "gpt-3.5-turbo"):
    openai.api_key = api_key
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ ChatGPT 応答エラー: {e}"
