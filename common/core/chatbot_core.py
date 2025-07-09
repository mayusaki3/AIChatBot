import os
from ai.chatgpt.openai_handler import chat_with_openai

def get_chat_response(api_key: str, prompt: str) -> str:
    # 明示されたAPIキーがなければ .env から取得
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
    return chat_with_openai(api_key, prompt)
