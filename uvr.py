import os
import shutil
import random
import string
import subprocess
import time
import requests
from urllib.parse import urlparse

def generate_random_identifier(length=8):
    """랜덤 식별자 생성 함수를 최상위 레벨로 이동"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

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

async def separate_audio_tracks(input_file_path, identifier):
    """
    주어진 mp3 파일을 vocal, MR, chorus로 분리하는 함수
    
    Args:
        input_file_path (str): 입력 mp3 파일의 경로
        identifier (str): 작업 폴더 식별자
    """
    # 기존 임시 폴더 사용
    temp_dir = os.path.join(os.getcwd(), "temp", identifier)
    temp_file_path = os.path.join(temp_dir, f"{identifier}.mp3")
    
    # 입력 파일을 임시 디렉토리로 복사
    shutil.copy2(input_file_path, temp_file_path)
    
    # 1단계: Kim Vocal 1 분리
    print("Separating with Kim Vocal 1...")
    subprocess.run([
        "audio-separator", temp_file_path, 
        "-m", "Kim_Vocal_1.onnx",
        "--output_dir", temp_dir,
        "--output_format", "mp3",
        "--normalization", "0.9",
        "--mdx_segment_size", "256",
        "--mdx_overlap", "0.25"
    ], check=True)
    time.sleep(2)
    
    # 2단계: 6HP-Karaoke 분리
    vocals_path = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1.mp3"
    print("Applying 6HP-Karaoke separation...")
    subprocess.run([
        "audio-separator", vocals_path,
        "-m", "6_HP-Karaoke-UVR.pth",
        "--output_dir", temp_dir,
        "--output_format", "mp3",
        "--normalization", "0.9",
        "--vr_window_size", "320",
        "--vr_aggression", "10"
    ], check=True)
    time.sleep(2)
    
    # 3단계: Reverb 적용
    karaoke_vocals_path = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
    print("Applying Reverb...")
    subprocess.run([
        "audio-separator", karaoke_vocals_path,
        "-m", "Reverb_HQ_By_FoxJoy.onnx",
        "--output_dir", temp_dir,
        "--output_format", "mp3",
        "--normalization", "0.9",
        "--mdx_segment_size", "256",
        "--mdx_overlap", "0.25"
    ], check=True)
    time.sleep(2)
    
    # 4단계: Denoising 적용
    reverb_path = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy.mp3"
    print("Applying Denoising...")
    subprocess.run([
        "audio-separator", reverb_path,
        "-m", "UVR-DeNoise.pth",
        "--output_dir", temp_dir,
        "--output_format", "mp3",
        "--normalization", "0.9",
        "--vr_window_size", "320",
        "--vr_aggression", "10"
    ], check=True)
    time.sleep(2)
    
    # 결과 파일 경로 반환
    result_paths = {
        'mr': f"{temp_dir}/{identifier}_(Instrumental)_Kim_Vocal_1.mp3",
        'chorus': f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3",
        'vocal': f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3"
    }
    
    return result_paths