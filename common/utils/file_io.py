import json

def parse_auth_file(file_bytes: bytes) -> dict:
    try:
        return json.loads(file_bytes.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}
