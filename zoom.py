import os
import jwt
import requests
import json
from datetime import datetime, timedelta

# 환경 변수 설정 (API 키와 비밀 키)
API_KEY = 'YOUR_ZOOM_API_KEY'
API_SECRET = 'YOUR_ZOOM_API_SECRET'

# JWT 생성 함수
def generate_jwt(api_key, api_secret):
    token = jwt.encode(
        {
            'iss': api_key,
            'exp': datetime.utcnow() + timedelta(minutes=60)
        },
        api_secret,
        algorithm='HS256'
    )
    return token

# 회의 생성 함수
def create_zoom_meeting(token):
    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }

    meeting_details = {
        "topic": "회의 주제",
        "type": 2,
        "start_time": (datetime.utcnow() + timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": "30",  # 회의 지속 시간 (분)
        "timezone": "Asia/Seoul",
        "agenda": "회의 설명",
        "settings": {
            "host_video": "true",
            "participant_video": "true",
            "join_before_host": "false",
            "mute_upon_entry": "true",
            "watermark": "true",
            "use_pmi": "false",
            "approval_type": 1,
            "audio": "voip",
            "auto_recording": "none"
        }
    }

    response = requests.post(
        'https://api.zoom.us/v2/users/me/meetings',
        headers=headers,
        data=json.dumps(meeting_details)
    )

    return response.json()

# 닉네임 포함 링크 생성 함수
def generate_join_url(meeting_info, nickname):
    join_url = meeting_info['join_url']
    join_url_with_nickname = f"{join_url}?uname={nickname}"
    return join_url_with_nickname

# 메인 실행 흐름
if __name__ == "__main__":
    token = generate_jwt(API_KEY, API_SECRET)
    meeting_info = create_zoom_meeting(token)
    nickname = "지정한닉네임"
    join_url_with_nickname = generate_join_url(meeting_info, nickname)

    print("회의 참가 링크:", join_url_with_nickname)
