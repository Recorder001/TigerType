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
    """타이핑 기록 저장. 모든 기록을 저장하고, 포럼에서 최고 기록만 표시."""
    record["uid"] = uid
    record["timestamp"] = int(time.time())
    db.child("records").push(record, token)


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
