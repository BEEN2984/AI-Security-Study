import json
from tools import TRACE

# allow_list 불러오기
with open("json/allow_list.json", "r", encoding="utf-8") as f:
    ALLOW_LIST = json.load(f)


def check_policy(tool_name, tool_args) -> str:
    decision = "deny"
    # 파일 관련 도구
    file_tools = ["read_file", "write_file", "delete_file"]
    if tool_name in file_tools:
        path = tool_args.get("path")

        if path in ALLOW_LIST["allowed_files"]:
            decision = "allow"

    # URL 요청
    elif tool_name == "http_get":
        url = tool_args.get("url")

        if url in ALLOW_LIST["allowed_urls"]:
            decision = "allow"


    # 송금 도구
    elif tool_name == "transfer_money":
        account = tool_args.get("to_account")

        if account in ALLOW_LIST["allowed_accounts"]:
            decision = "allow"


    TRACE.append({
        "tool": tool_name,
        "args": tool_args,
        "policy": decision
    })

    return decision