from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, ClassVar, List
from common.actions.action_utils import parse_tool_json, coerce_queries, coerce_top_k, coerce_recency_days
import json

@dataclass
class WebSearchAction:
    tool: ClassVar[str] = "web.search"

    queries: List[str] = field(default_factory=list)
    top_result: int = 5
    recency_days: Optional[int] = None
    lang: Optional[str] = None
    require_citations: bool = True

    # LM出力テキストが WebSearchAction の JSON ならパースして返す。そうでなければ None。
    @classmethod
    def parse(cls, text: str) -> Optional["WebSearchAction"]:
        obj = parse_tool_json(text, expected_tool="web.search")
        if not obj:
            return None

        queries = coerce_queries(obj)
        if not queries:
            return None

        top_result = coerce_top_k(obj.get("top_result", obj.get("top_k", 5)))
        recency_days = coerce_recency_days(obj)
        require_citations = bool(obj.get("require_citations", True))

        return cls(
            queries=queries,
            top_result=top_result,
            recency_days=recency_days,
            lang=(obj.get("lang") or None),
            require_citations=require_citations,
        )
