import os
import requests
import string
import random

async def download_mp3(url, song_request_id, file_number):
    """
    URL에서 MP3 파일을 다운로드하여 지정된 경로에 저장
    
    Args:
        url (str): 다운로드할 MP3 파일의 URL
        song_request_id (str): 노래 요청 ID
        file_number (int): 파일 번호 (1 또는 2)
    """
    # 저장 경로 설정
    temp_dir = os.path.join('/app/temp', str(song_request_id))
    os.makedirs(temp_dir, exist_ok=True)
    
    save_path = os.path.join(temp_dir, f'original{file_number}.mp3')
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

def generate_random_identifier(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))