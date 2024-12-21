import requests

async def generate_audio(lyric: str):
    url = "https://api.acedata.cloud/suno/audios"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer 745f1ba0209d4f078897ffe720dc1f77",
        "content-type": "application/json"
    }

    payload = {
        "action": "generate",
        "model": "chirp-v4",
        "lyric": "누구나 한 번쯤은 자기만의 세계로 빠져들게 되는 순간이 있지 그렇지만 나는 제자리로 오지 못했어 되돌아 나오는 길을 모르니 너무 많은 생각과 너무 많은 걱정에 온통 내 자신을 가둬두었지 이젠 이런 내 모습 나조차 불안해 보여 어디부터 시작할지 몰라서",
        "custom": True,
        "instrumental": False,
        "title": "비상",
        "style": "rock",
        "style_negative": "ballad,dance"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)