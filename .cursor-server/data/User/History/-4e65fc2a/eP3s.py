import os
import shutil
import random
import string
import subprocess
import time
import requests
import gc
import torch
from urllib.parse import urlparse
from audio_separator.separator import Separator

# GPU 메모리 파편화를 방지하기 위한 환경 변수 설정
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def generate_random_identifier(length=8):
    """랜덤 식별자 생성 함수를 최상위 레벨로 이동"""
    import string
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
    
    separator = Separator(**base_params)
    
    # 1단계: Kim Vocal 1 분리
    try:
        print("Separating with Kim Vocal 1...")
        separator.load_model(model_filename='Kim_Vocal_1.onnx')
        separator.separate(temp_file_path)
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        time.sleep(2)
        
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("CUDA 메모리 부족 에러 발생 - Kim Vocal 1 분리 중.")
        raise e
    finally:
        gc.collect()
        torch.cuda.empty_cache()
    
    # Kim Vocal 1 결과 파일 경로 저장
    vocals_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1.mp3"
    
    time.sleep(2)
    
    # 2단계: 6HP-Karaoke 분리
    try:
        print("Applying 6HP-Karaoke separation...")
        # 새 인스턴스를 다시 생성(추가 메모리 해제)
        separator = Separator(**base_params)
        separator.load_model(model_filename='6_HP-Karaoke-UVR.pth')
        separator.separate(vocals_path)
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        time.sleep(2)
        
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("CUDA 메모리 부족 에러 발생 - 6HP-Karaoke 분리 중.")
        raise e
    finally:
        gc.collect()
        torch.cuda.empty_cache()
    
    # 3단계: Reverb 적용
    karaoke_vocals_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
    
    try:
        print("Applying Reverb...")
        separator.load_model(model_filename='Reverb_HQ_By_FoxJoy.onnx')
        separator.separate(karaoke_vocals_path)
        torch.cuda.empty_cache()
        time.sleep(2)
        
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("CUDA 메모리 부족 에러 발생 - Reverb 적용 중.")
        raise e
    finally:
        gc.collect()
        torch.cuda.empty_cache()
    
    # 4단계: Denoising 적용
    reverb_path = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy.mp3"
    
    try:
        print("Applying Denoising...")
        separator.load_model(model_filename='UVR-DeNoise.pth')
        separator.separate(reverb_path)
        torch.cuda.empty_cache()
        time.sleep(2)
        
    except RuntimeError as e:
        if "CUDA out of memory" in str(e):
            print("CUDA 메모리 부족 에러 발생 - Denoising 적용 중.")
        raise e
    finally:
        gc.collect()
        torch.cuda.empty_cache()
    
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