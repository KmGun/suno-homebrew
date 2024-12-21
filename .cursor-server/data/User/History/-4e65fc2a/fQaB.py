import os
import shutil
import random
import string
import subprocess
import time
import requests
from urllib.parse import urlparse
from audio_separator.separator import Separator
import torch


def generate_random_identifier(length=8):
    """랜덤 식별자 생성 함수를 최상위 레벨로 이동"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def separate_audio_tracks(input_file_path, song_request_id, file_number):
    """
    주어진 mp3 파일을 vocal, MR, chorus로 분리하는 함수
    
    Args:
        input_file_path (str): 입력 mp3 파일의 경로
        song_request_id (str): 노래 요청 ID
        file_number (int): 파일 번호 (1 또는 2)
    """
    # 작업 디렉토리 설정
    temp_dir = os.path.join('/app/temp', str(song_request_id))
    temp_file_path = os.path.join(temp_dir, f"temp_{file_number}.mp3")
    
    # 입력 파일을 임시 파일로 복사
    shutil.copy2(input_file_path, temp_file_path)
    
    # 공통 설정
    base_params = {
        'output_dir': temp_dir,
        'output_format': 'mp3',
        'normalization_threshold': 0.9,
        'model_file_dir': '/app/models'
    }
    
    # Separator 인스턴스 생성
    separator = Separator(**base_params)
    
    # 1단계: Kim Vocal 1 분리
    print("Separating with Kim Vocal 1...")
    separator.load_model(model_filename='Kim_Vocal_1.onnx')
    separator.separate(temp_file_path)
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    time.sleep(2)
    
    # Kim Vocal 1 결과 파일 경로 저장
    vocals_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1.mp3"
    
    torch.cuda.empty_cache()  # GPU 메모리 정리
    time.sleep(2)
    
    # 2단계: 6HP-Karaoke 분리
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    time.sleep(5)
    
    print("Applying 6HP-Karaoke separation...")
    separator = Separator(**base_params)
    separator.load_model(model_filename='6_HP-Karaoke-UVR.pth')
    separator.separate(vocals_path)
    torch.cuda.empty_cache()
    torch.cuda.synchronize()
    time.sleep(2)
    
    # 3단계: Reverb 적용
    karaoke_vocals_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
    print("Applying Reverb...")
    separator.load_model(model_filename='Reverb_HQ_By_FoxJoy.onnx')
    separator.separate(karaoke_vocals_path)
    torch.cuda.empty_cache()  # GPU 메모리 정리
    time.sleep(2)
    
    # 4단계: Denoising 적용
    reverb_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy.mp3"
    print("Applying Denoising...")
    separator.load_model(model_filename='UVR-DeNoise.pth')
    separator.separate(reverb_path)
    torch.cuda.empty_cache()  # GPU 메모리 정리
    time.sleep(2)
    
    # 결과 파일 경로 설정 (파일 번호를 앞으로 이동)
    result_paths = {
        'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
        'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
        'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
    }
    
    # 처리된 파일들을 원하는 이름으로 복사
    shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Instrumental)_Kim_Vocal_1.mp3", 
                result_paths['mr'])
    shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3", 
                result_paths['chorus'])
    shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3", 
                result_paths['vocal'])
    
    return result_paths