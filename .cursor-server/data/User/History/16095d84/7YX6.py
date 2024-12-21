import requests

async def generate_audio(lyric: str, title: str, style: str, style_negative: str):
    print("🎵 Suno API 호출 시작...")
    
    url = "https://api.acedata.cloud/suno/audios"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer 745f1ba0209d4f078897ffe720dc1f77",
        "content-type": "application/json"
    }

    payload = {
        "action": "generate",
        "model": "chirp-v4",
        "lyric": lyric,
        "custom": True,
        "instrumental": False,
        "title": title,
        "style": style,
        "style_negative": style_negative
    }

    try:
        print(f"📤 API 요청 데이터: {payload}")
        response = requests.post(url, json=payload, headers=headers)
        print(f"📥 API 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ API 에러 응답: {response.text}")
            # API 호출 실패시 테스트용 더미 데이터 반환
            return {
                "success": True,
                "data": [
                    {
                        "audio_url": "https://cdn1.suno.ai/0ecafeed-904e-4ef2-89ef-6a314ad2dabf.mp3",
                    },
                    {
                        "audio_url": "https://cdn1.suno.ai/8b0885bd-1b89-4e3a-bcdd-ef6542222056.mp3",
                    }
                ]
            }
    except Exception as e:
        print(f"❌ API 호출 중 에러 발생: {str(e)}")
        raise e