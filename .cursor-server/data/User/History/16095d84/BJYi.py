import requests

async def generate_audio(lyric: str, title: str, style: str, style_negative: str):
    print("🎵 Suno API 호출 시작...")
    print(f"📝 입력값 확인:")
    print(f"   - 가사: {lyric}")
    print(f"   - 제목: {title}")
    print(f"   - 스타일: {style}")
    print(f"   - 네거티브 스타일: {style_negative}")
    
    # API 호출 부분 주석 처리
    # url = "https://api.acedata.cloud/suno/audios"
    # headers = {...}
    # payload = {...}
    # response = requests.post(url, json=payload, headers=headers)
    
    # 하드코딩된 테스트 데이터 반환
    test_result = {
        "success": True,
        "task_id": "test-task-id",
        "trace_id": "test-trace-id",
        "data": [
            {
                "id": "test-id-1",
                "title": title,
                "audio_url": "https://cdn1.suno.ai/0ecafeed-904e-4ef2-89ef-6a314ad2dabf.mp3",
                "state": "succeeded"
            },
            {
                "id": "test-id-2",
                "title": title,
                "audio_url": "https://cdn1.suno.ai/8b0885bd-1b89-4e3a-bcdd-ef6542222056.mp3",
                "state": "succeeded"
            }
        ]
    }
    
    print("✅ 테스트 데이터 반환")
    print(f"📦 반환 데이터: {test_result}")
    return test_result