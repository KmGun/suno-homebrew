import requests

async def generate_audio(lyric: str,title : str,style : str,style_negative : str):
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

    response = requests.post(url, json=payload, headers=headers)
    # result = response.json()
    result =
    {
    "success": true,
    "task_id": "34e2da5f-088e-4562-b3e2-4be6ea26f1e6",
    "trace_id": "df59156e-f3cd-44b7-83f0-6d042c72ed53",
    "data": [
        {
        "id": "0ecafeed-904e-4ef2-89ef-6a314ad2dabf",
        "title": "비상",
        "image_url": "https://cdn2.suno.ai/image_0ecafeed-904e-4ef2-89ef-6a314ad2dabf.jpeg",
        "lyric": "누구나 한 번쯤은 자기만의 세계로 빠져들게 되는 순간이 있지 그렇지만 나는 제자리로 오지 못했어 되돌아 나오는 길을 모르니 너무 많은 생각과 너무 많은 걱정에 온통 내 자신을 가둬두었지 이젠 이런 내 모습 나조차 불안해 보여 어디부터 시작할지 몰라서",
        "audio_url": "https://cdn1.suno.ai/0ecafeed-904e-4ef2-89ef-6a314ad2dabf.mp3",
        "video_url": "https://cdn1.suno.ai/0ecafeed-904e-4ef2-89ef-6a314ad2dabf.mp4",
        "created_at": "2024-12-18T10:56:57.034Z",
        "model": "chirp-v4",
        "state": "succeeded",
        "style": "rock",
        "duration": 188.28
        },
        {
        "id": "8b0885bd-1b89-4e3a-bcdd-ef6542222056",
        "title": "비상",
        "image_url": "https://cdn2.suno.ai/image_8b0885bd-1b89-4e3a-bcdd-ef6542222056.jpeg",
        "lyric": "누구나 한 번쯤은 자기만의 세계로 빠져들게 되는 순간이 있지 그렇지만 나는 제자리로 오지 못했어 되돌아 나오는 길을 모르니 너무 많은 생각과 너무 많은 걱정에 온통 내 자신을 가둬두었지 이젠 이런 내 모습 나조차 불안해 보여 어디부터 시작할지 몰라서",
        "audio_url": "https://cdn1.suno.ai/8b0885bd-1b89-4e3a-bcdd-ef6542222056.mp3",
        "video_url": "https://cdn1.suno.ai/8b0885bd-1b89-4e3a-bcdd-ef6542222056.mp4",
        "created_at": "2024-12-18T10:56:57.035Z",
        "model": "chirp-v4",
        "state": "succeeded",
        "style": "rock",
        "duration": 137.8
        }
    ]
    }
   
    return response.text