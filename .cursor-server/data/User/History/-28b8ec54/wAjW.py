async def download_mp3(url):
    """URL에서 MP3 파일을 다운로드하여 로컬에 저장"""
    # 랜덤 식별자로 임시 작업 폴더 생성
    identifier = generate_random_identifier(8)
    temp_dir = os.path.join(os.getcwd(), "temp", identifier)
    os.makedirs(temp_dir, exist_ok=True)
    
    # URL에서 파일명 추출
    filename = os.path.basename(urlparse(url).path)
    save_path = os.path.join(temp_dir, filename)
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path, identifier  # identifier도 함께 반환
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

def generate_random_identifier(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))