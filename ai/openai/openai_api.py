from openai import AsyncOpenAI
from typing import Optional

# メイン関数：ChatGPTにメッセージ送信
async def call_chatgpt(context_list: list[dict], api_key: str, model: str = "gpt-3.5-turbo") -> str:
    messages = []
    for msg in context_list:
        if msg.startswith("AIChatBot:"):
            messages.append({"role": "assistant", "content": msg.replace("AIChatBot:", "", 1).strip()})
        else:
            messages.append({"role": "user", "content": msg})
 
    try:
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ OpenAI 応答エラー: {e}"
