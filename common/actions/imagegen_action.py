from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict, ClassVar
from common.actions.action_utils import parse_tool_json
import json

@dataclass
class ImageGenAction:
    tool: ClassVar[str] = "image.generate"

    prompt: str
    success_message: str = "🖼️ 画像を生成しました。"
    failure_message: str = "⚠️ 画像生成に失敗しました。"

    # LM出力テキストが ImageGenAction の JSON ならパースして返す。そうでなければ None。
    @classmethod
    def parse(cls, text: str) -> Optional["ImageGenAction"]:
        obj = parse_tool_json(text, expected_tool="image.generate")
        if not obj:
            return None
        prompt = (obj.get("prompt") or "").strip()
        if not prompt:
            return None
        return cls(
            prompt=prompt,
            success_message=obj.get("success_message") or "🖼️ 画像を生成しました。",
            failure_message=obj.get("failure_message") or "⚠️ 画像生成に失敗しました。",
        )
