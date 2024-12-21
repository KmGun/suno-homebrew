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
   
    return response.text