# 외부 출처 데이터에 오염 태그를 붙이고, 위험 sink 도달 시 차단한다.

# 신뢰하지 않는 데이터 출처
UNTRUSTED_SOURCES = {"file", "web", "tool_output", "email"}

# 오염된 데이터가 들어가면 위험한 도구 인자
DANGEROUS_SINKS = {
    "transfer_money": ["to_account"],
    "http_get": ["url"],
    "write_file": ["path"],
    "delete_file": ["path"],
}

# untrusted 데이터 저장
TAINTED_DATA = []

class TaintViolation(Exception):
    pass

# -------------------------------------------------
# 외부 출처 데이터를 tainted 데이터로 등록
def register_tainted_data(value, source, detail=None):

    if source not in UNTRUSTED_SOURCES:
        return

    TAINTED_DATA.append({
        "value": str(value),
        "source": source,
        "detail": detail
    })

# -------------------------------------------------
# 값이 비신뢰 데이터에서 나온 것인지 확인
def find_taint(value):

    value = str(value)

    for data in TAINTED_DATA:
        if value in data["value"]:
            return data

    return None

# -------------------------------------------------
# 위험 sink 검사
def check_taint_tool_call(tool_name, kwargs):

    dangerous_args = DANGEROUS_SINKS.get(tool_name, [])

    for arg_name in dangerous_args:

        value = kwargs.get(arg_name)

        if value is None:
            continue

        taint_info = find_taint(value)

        if taint_info is not None:
            raise TaintViolation(
                f"blocked: {tool_name}.{arg_name}={value} "
                f"<- {taint_info['source']} "
                f"({taint_info['detail']})"
            )

        





