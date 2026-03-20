# firebase_config.py — Firebase 설정
#
# ★★★ 사용법 ★★★
# 1. https://console.firebase.google.com/ 에서 프로젝트 생성
# 2. 프로젝트 설정 → 일반 → 하단의 "웹 앱 추가" 클릭
# 3. 앱 이름 입력 후 등록 → firebaseConfig 값을 아래에 붙여넣기
# 4. 왼쪽 메뉴 "빌드" → "Authentication" → "시작하기" 클릭
#    → "이메일/비밀번호" 로그인 방법 사용 설정
# 5. 왼쪽 메뉴 "빌드" → "Realtime Database" → "데이터베이스 만들기"
#    → 테스트 모드로 시작 (나중에 보안 규칙 수정)
#
# 아래 값들을 본인의 Firebase 프로젝트 값으로 교체하세요:

FIREBASE_CONFIG = {
    "apiKey": "AIzaSyDHJeJiAkW3T-EJAY_CM4m5If0TeJBDPbU",
    "authDomain": "tigertype-c66fd.firebaseapp.com",
    "databaseURL": "https://tigertype-c66fd-default-rtdb.asia-southeast1.firebasedatabase.app",
    "storageBucket": "tigertype-c66fd.firebasestorage.app",
}
