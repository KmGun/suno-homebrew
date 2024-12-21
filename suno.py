import requests

async def generate_audio(lyric: str, title: str, style: str, style_negative: str):
    print("🎵 Suno API 호출 시작...")
    print(f"📝 입력값 확인:")
    print(f"   - 가사: {lyric}")
    print(f"   - 제목: {title}")
    print(f"   - 스타일: {style}")
    print(f"   - 네거티브 스타일: {style_negative}")
    
    # API 호출 부분
    url = "https://api.acedata.cloud/suno/audios"
    headers = {
    "accept": "application/json",
    "authorization": "Bearer 745f1ba0209d4f078897ffe720dc1f77",
    "content-type": "application/json"
    }
    payload = {
        "action": "generate",
        "model": "chirp-v4",
        "lyric": "좁고 좁은 저 문으로 들어가는 길은 나를 깎고 잘라서 스스로 작아지는 것뿐 이젠 버릴것조차 거의 남은게 없는데 문득 거울을 보니 자존심 하나가 남았네 두고온 고향 보고픈 얼굴 따뜻한 저녁과 웃음 소리 고갤 흔들어 지워버리며 소리를 듣네 나를 부르는 쉬지말고 가라하는 저 강들이 모여드는 곳 성난 파도 아래 깊이 한 번 만이라도 이를 수 있다면 나 언젠가 심장이 터질 때까지 흐느껴 울고 웃다가 긴 여행을 끝내리 미련없이 익숙해가는 거친 잠자리도 또 다른 안식을 빚어 그마저 두려울 뿐인데 부끄러운 게으름 자잘한 욕심들아 얼마나 나일 먹어야 마음의 안식을 얻을까 하루 또 하루 무거워지는 고독의 무게를 참는 것은 그보다 힘든 그보다 슬픈 의미도 없이 잊혀지긴 싫은 두려움 때문이지만 저 강들이 모여 드는 곳 성난 파도 아래 깊이 한 번 만이라도 이를 수 있다면 나 언젠가 심장이 터질 때까지 흐느껴 울고 웃으며 긴 여행을 끝내리 미련없이 아무도 내게 말해 주지 않은 정말로 내가 누군지 알기 위해",
        "custom": True,
        "instrumental": False,
        "title": "민물장어의 꿈 2",
        "style": "rock, ballad",
        "style_negative": "fork, blues"
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    # 하드코딩된 테스트 데이터 반환
    # test_result = {
    #     "success": True,
    #     "task_id": "test-task-id",
    #     "trace_id": "test-trace-id",
    #     "data": [
    #         {
    #             "id": "test-id-1",
    #             "title": title,
    #             "audio_url": "https://cdn1.suno.ai/0ecafeed-904e-4ef2-89ef-6a314ad2dabf.mp3",
    #             "state": "succeeded"
    #         },
    #         {
    #             "id": "test-id-2",
    #             "title": title,
    #             "audio_url": "https://cdn1.suno.ai/8b0885bd-1b89-4e3a-bcdd-ef6542222056.mp3",
    #             "state": "succeeded"
    #         }
    #     ]
    # }
    
    print("✅ 테스트 데이터 반환")
    print(f"📦 반환 데이터: {response_data}")
    return response_data