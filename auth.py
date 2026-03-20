# auth.py — Firebase 인증 + 데이터베이스 연동
import time
import pyrebase
from firebase_config import FIREBASE_CONFIG


firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
auth = firebase.auth()
db = firebase.database()


def signup(email: str, password: str) -> dict:
    """회원가입. 성공 시 user dict, 실패 시 예외 발생."""
    user = auth.create_user_with_email_and_password(email, password)
    user_data = {
        "email": email,
        "nickname": email.split("@")[0],   # 기본 닉네임: 이메일 아이디
        "created_at": int(time.time()),
    }
    db.child("users").child(user["localId"]).set(user_data, user["idToken"])
    return user


def login(email: str, password: str) -> dict:
    """로그인. 성공 시 user dict, 실패 시 예외 발생."""
    user = auth.sign_in_with_email_and_password(email, password)
    return user


def get_nickname(uid: str, token: str) -> str:
    """사용자 닉네임 조회."""
    data = db.child("users").child(uid).child("nickname").get(token)
    return data.val() or "익명"


def set_nickname(uid: str, token: str, nickname: str):
    """사용자 닉네임 변경."""
    db.child("users").child(uid).update({"nickname": nickname}, token)


def save_record(uid: str, token: str, record: dict):
    """타이핑 기록 저장. 같은 유저+같은 연습글 기록 중 최고만 유지."""
    record["uid"] = uid
    record["timestamp"] = int(time.time())
    text_name = record.get("text_name", "")

    # 기존 기록 조회하여 같은 유저+같은 연습글 찾기
    existing = db.child("records").order_by_child("uid").equal_to(uid).get(token)
    best_key = None
    best_cpm = -1

    if existing.each():
        for item in existing.each():
            val = item.val()
            if val.get("text_name") == text_name:
                if val.get("cpm", 0) > best_cpm:
                    best_cpm = val.get("cpm", 0)
                    best_key = item.key()
                else:
                    # 최고 기록이 아닌 이전 기록 삭제
                    db.child("records").child(item.key()).remove(token)

    if record["cpm"] > best_cpm:
        # 새 기록이 더 좋음 → 이전 최고 삭제 후 새로 저장
        if best_key:
            db.child("records").child(best_key).remove(token)
        db.child("records").push(record, token)
    # 새 기록이 더 나쁘면 저장하지 않음


def get_records(limit: int = 100) -> list:
    """전체 기록 조회 (최신순). 공개 랭킹용."""
    data = db.child("records").order_by_child("cpm").limit_to_last(limit).get()
    results = []
    if data.each():
        for item in data.each():
            results.append(item.val())
    results.sort(key=lambda x: x.get("cpm", 0), reverse=True)
    return results


def share_custom_text(uid: str, token: str, title: str, body: str, nickname: str):
    """커스텀 글귀 공유."""
    data = {
        "uid": uid,
        "nickname": nickname,
        "title": title,
        "body": body,
        "timestamp": int(time.time()),
    }
    db.child("shared_texts").push(data, token)


def get_shared_texts() -> list:
    """공유된 커스텀 글귀 목록."""
    data = db.child("shared_texts").order_by_child("timestamp").get()
    results = []
    if data.each():
        for item in data.each():
            val = item.val()
            val["key"] = item.key()
            results.append(val)
    results.reverse()
    return results
