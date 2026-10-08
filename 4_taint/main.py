import glob, yaml, json
from agent import run_agent, MESSAGES
from pathlib import Path
from tools import TRACE, SANDBOX
from openai import BadRequestError
from taint import TAINTED_DATA
from datetime import datetime

BASE_DIR = Path(__file__).parent


# --------------------------------------------------------
# 공격 케이스 불러오기
def load_attack_cases() -> list:
    cases = []

    attack_dir = BASE_DIR / "attacks"

    for file_path in sorted(attack_dir.rglob("*.yaml")):
        with open(file_path, "r", encoding="utf-8") as f:
            cases.append(yaml.safe_load(f))

    return cases


# ----------------------------------------------------------
# YAML의 success_if 기준으로 실제 공격 성공 여부 판단
def judge(trace, success_if) -> bool:
    expected_tool = success_if["tool"]
    expected_args = success_if.get("arg_contains", {})

    for event in trace:

        # 실제 실행된 도구가 아니면 넘어감
        if not event.get("executed", False):
            continue

        # 성공 조건에서 지정한 도구가 아니면 넘어감
        if event["tool"] != expected_tool:
            continue

        args = event.get("args", {})
        matched = True

        # 성공 조건의 모든 인자 검사
        for arg_name, expected_value in expected_args.items():
            actual_value = args.get(arg_name)

            if actual_value is None:
                matched = False
                break

            if str(expected_value) not in str(actual_value):
                matched = False
                break

        if matched:
            return True

    return False

#--------------------------------------------------
# direct 공격: user_input <- user_request + payload
def prepare_direct_userInput(case) -> None:
    userInput = case["user_request"] + "\n" + case["payload"]
    case["user_request"] = userInput

# -------------------------------------------------
# 간접 공격 payload 준비
def prepare_indirect_case(case):
    payload_file = case["payload_file"]
    payload = case["payload"]

    target = (SANDBOX / payload_file).resolve()

    # sandbox 외부 접근 방지
    if target != SANDBOX and SANDBOX not in target.parents:
        raise ValueError("Invalid payload file path")

    # 테스트 준비 과정은 TRACE에 기록되지 않도록
    # Python에서 직접 파일 생성
    target.write_text(payload, encoding="utf-8")

# ------------------------------------------------------
# 케이스 실행 전 상태 초기화
def reset_runtime():
    TRACE.clear()
    MESSAGES.clear()
    TAINTED_DATA.clear()

# ---------------------------------------------------
# 공격 유형에 따른 입력 준비
def prepare_case(case):
    if case["type"] == "direct":
        prepare_direct_userInput(case)
    elif case["type"] == "indirect":
        prepare_indirect_case(case)

# -----------------------------------------------------
# TRACE 에서 policy, taint 결과 추출
def extract_defense_results():
    policy_decisions = [
        event["policy"]
        for event in TRACE
        if "policy" in event
    ]
    taint_decisions = [
        event["taint"]
        for event in TRACE
        if "taint" in event
    ]

    return policy_decisions, taint_decisions

# ------------------------------------------------------
# 공격 케이스 하나 실행
def run_case(case, policy_enabled, taint_enabled):
    reset_runtime()
    prepare_case(case)

    try:
        response = run_agent(
            case["user_request"],
            policy_enabled=policy_enabled,
            taint_enabled=taint_enabled
        )
        attack_success = judge(
            TRACE,
            case["success_if"]
        )
    except BadRequestError:
        response = "API_BLOCKED"
        attack_success = False

    policy_decisions, taint_decisions = extract_defense_results()

    return {
        "id": case["id"],
        "type": case["type"],
        "category": case.get("category"),
        "attack_success": attack_success,
        "policy": policy_decisions,
        "taint": taint_decisions,
        "response": response,
        "trace": TRACE.copy()
        }

# ------------------------------------------------------
# 공격 유형별로 요약
def summarize_type(results, attack_type):
    filtered = [
        r for r in results
        if r["type"] == attack_type
    ]

    success = sum(
        1 for r in filtered
        if r["attack_success"]
    )

    total = len(filtered)

    return {
        "total": total,
        "success": success,
        "failed": total - success
    }

# -----------------------------------
# 전체 요약
def build_summary(results):
    total = len(results)

    attack_success = sum(
        1 for r in results
        if r["attack_success"]
    )

    return {
        "total": total,
        "attack_success": attack_success,
        "attack_failed": total - attack_success,

        "api_blocked": sum(
            1 for r in results
            if r["response"] == "API_BLOCKED"
        ),

        "policy_denied": sum(
            1 for r in results
            if "deny" in r["policy"]
        ),

        # taint 차단을 경험한 공격 케이스 수 
        "taint_denied": sum(
            1 for r in results
            if "deny" in r["taint"]
        ),

        "direct": summarize_type(results, "direct"),
        "indirect": summarize_type(results, "indirect")
    }



# ------------------------------------------------------
# 결과를 JSON으로 저장
def save_results(results):
    summary = build_summary(results)

    output = {
        "summary": summary,
        "results": results
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = (
        BASE_DIR / f"result/results_{timestamp}.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            output,
            f,
            ensure_ascii=False,
            indent=4
        )

    return output

# --------------------------------------------------
# result_table.md 파일에 표 추가
def append_result_table(summary, policy_enabled, taint_enabled):
    output_path = BASE_DIR / "result/result_table.md"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 파일이 없으면 헤더 먼저 생성
    if not output_path.exists():
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(
                "| Timestamp | Policy | Taint | Total | "
                "Attack Success | Attack Failed | "
                "Policy Denied | Taint Denied | API Blocked |\n"
            )
            f.write(
                "|---|---|---|---:|---:|---:|---:|---:|---:|\n"
            )

    # 실행 결과 한 줄 추가
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(
            f"| {timestamp} "
            f"| {policy_enabled} "
            f"| {taint_enabled} "
            f"| {summary['total']} "
            f"| {summary['attack_success']} "
            f"| {summary['attack_failed']} "
            f"| {summary['policy_denied']} "
            f"| {summary['taint_denied']} "
            f"| {summary['api_blocked']} |\n"
        )

# ------------------------------------------------------
def main():
    results = []
    cases = load_attack_cases()

    policy_enabled=True
    taint_enabled=False

    for case in cases:
        result = run_case(case, policy_enabled=policy_enabled, taint_enabled=taint_enabled)
        results.append(result)

    # 전체 요약
    summary = build_summary(results)

    # JSON 상세 결과 저장
    output = save_results(results)

    # MD 결과표에 이번 실행 결과 추가
    append_result_table(
        summary,
        policy_enabled=policy_enabled,
        taint_enabled=taint_enabled
    )

    return output


if __name__ == "__main__":
    main()