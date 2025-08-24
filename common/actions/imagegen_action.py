# common/actions/image_action.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict, ClassVar
import json

@dataclass
class ImageGenAction:
    prompt: str
    success_message: str = "🖼️ 画像を生成しました。"
    failure_message: str = "⚠️ 画像生成に失敗しました。"
    type: ClassVar[str] = "image.generate"

    @classmethod
    def parse(cls, text: str) -> Optional["ImageGenAction"]:
        text = text.strip()
        if not (text.startswith("{") and text.endswith("}")):
            return None
        try:
            obj: Dict[str, Any] = json.loads(text)
        except Exception:
            return None
        if obj.get("type") != "image.generate":
            return None
        prompt = obj.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return None
        return cls(
            prompt=prompt.strip(),
            success_message=obj.get("success_message") or "🖼️ 画像を生成しました。",
            failure_message=obj.get("failure_message") or "⚠️ 画像生成に失敗しました。",
        )
