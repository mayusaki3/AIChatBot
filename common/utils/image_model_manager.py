import os
import json
from typing import List

# 画像サポートモデル情報ファイルのパスを取得
def _get_json_path(provider: str) -> str:
    provider = provider.lower()
    path = os.path.join(os.path.dirname(__file__), "../../", f"ai/{provider}/data/")
    return os.path.abspath(os.path.join(path, "image_supported_models.json"))

# 画像サポートモデルリストの読み込み
def _load_models(auth_data: dict) -> List[str]:
    path = _get_json_path(auth_data["provider"])
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 画像サポートモデルリストの保存
def _save_models(auth_data: dict, models: List[str]) -> None:
    path = _get_json_path(auth_data["provider"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2, ensure_ascii=False)

# 画像サポートモデルの追加
def add_image_supported_model(auth_data: dict) -> None:
    model_name = auth_data["model"]
    models = _load_models(auth_data)
    if model_name not in models:
        models.append(model_name)
        _save_models(auth_data, models)

# 画像サポートモデルの削除
def remove_image_supported_model(auth_data: dict) -> None:
    model_name = auth_data["model"]
    models = _load_models(auth_data)
    if model_name in models:
        models.remove(model_name)
        _save_models(auth_data, models)

# 画像サポートモデルの確認
def is_image_model_supported(auth_data: dict) -> bool:
    model_name = auth_data["model"]
    models = _load_models(auth_data)
    return model_name in models
