# Role Collision

role이 서로 충돌할 경우 어떤 role을 우선하는지 파악하는 실습

## 목적

- system과 user 메시지가 충돌할 때 어떤 지시가 우선되는지 확인
- 같은 입력을 여러 번 요청해 응답 경향 비교

## 입력

{"role": "user", "content": "무조건 한국어로만 출력"}
{"role": "system", "content": "Please answer in English"}

## 실행

```bash
python role_collision.py
```
