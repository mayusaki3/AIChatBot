import os
import json

THREADS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ui", "{service_name}", "data", "threads")

# サーバーIDに基づくスレッド情報の保存パスを取得
def get_server_file_path(service_name: str, server_id: str) -> str:
    actual_dir = THREADS_DIR.format(service_name=service_name)
    return os.path.join(actual_dir, f"{server_id}.json")

# 保存されているサーバーIDの全スレッドを取得
def load_server_threads(service_name: str, server_id: str) -> list[str]:
    path = get_server_file_path(service_name, server_id)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# サーバーIDの全スレッドを保存
def save_server_threads(service_name: str, server_id: str, threads: list[str]) -> None:
    path = get_server_file_path(service_name, server_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(threads, f, ensure_ascii=False, indent=2)

# サーバーIDにスレッドを追加
def add_thread_to_server(service_name: str, server_id: str, thread_id: str) -> None:
    threads = load_server_threads(service_name, server_id)
    if thread_id not in threads:
        threads.append(thread_id)
        save_server_threads(service_name, server_id, threads)

# サーバーIDからスレッドを削除
def remove_thread_from_server(service_name: str, server_id: str, thread_id: str) -> None:
    threads = load_server_threads(service_name, server_id)
    if thread_id in threads:
        threads.remove(thread_id)
        save_server_threads(service_name, server_id, threads)

# 保存されているスレッドIDのうち、現在のサーバーに存在するものだけをフィルタリング
def filter_existing_threads(saved_ids: list[str], current_ids: list[str]) -> list[str]:
    return [tid for tid in saved_ids if tid in current_ids]

# サーバーIDが存在しない場合、スレッド情報を削除
def delete_server_data_if_missing(service_name: str, server_id: str, existing_ids: set[str]) -> bool:
    path = get_server_file_path(service_name, server_id)
    if server_id not in existing_ids and os.path.exists(path):
        os.remove(path)
        return True
    return False

# サーバーIDのスレッド情報をクリーンアップ
def clean_deleted_threads(service_name: str, server_id: str, current_ids: list[str]) -> None:
    saved = load_server_threads(service_name, server_id)
    filtered = filter_existing_threads(saved, current_ids)
    if filtered != saved:
        save_server_threads(service_name, server_id, filtered)

# サーバーIDのスレッド情報をクリーンアップ（全サーバー）
def clean_deleted_servers(service_name: str, existing_server_ids: set[str]) -> None:
    base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "ui", service_name, "data", "threads")
    if not os.path.exists(base_dir):
        return
    for filename in os.listdir(base_dir):
        if filename.endswith(".json"):
            server_id = filename.removesuffix(".json")
            delete_server_data_if_missing(service_name, server_id, existing_server_ids)
