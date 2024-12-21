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

# 기본 CUDA 메모리 관리 설정
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def clear_gpu_memory():
    """GPU 메모리 정리"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

class MemoryEfficientSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
        self.base_params = {
            'output_format': 'mp3',
            'normalization_threshold': 0.9,
            'model_file_dir': f'{base_dir}/models',
            'device_type': 'cuda',
            'batch_size': 1,
            'overlap': 0.1
        }
        
    def _create_separator(self, temp_dir):
        """분리기 생성"""
        params = self.base_params.copy()
        params['output_dir'] = temp_dir
        return Separator(**params)

    async def process_stage(self, input_path, model_name, temp_dir, stage_name):
        """단계별 처리"""
        print(f"Starting {stage_name} with {model_name}...")
        
        # Denoising 단계에서 입력 파일명 수정
        if stage_name == "Denoising":
            base_dir = os.path.dirname(input_path)
            file_number = os.path.basename(input_path).split('_')[1]
            input_path = os.path.join(base_dir, f"temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3")
        
        if not os.path.exists(input_path):
            print(f"Looking for input file: {input_path}")
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            clear_gpu_memory()
            separator = self._create_separator(temp_dir)
            separator.load_model(model_filename=model_name)
            separator.separate(input_path)
            clear_gpu_memory()
            
            return True
            
        except RuntimeError as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        """오디오 트랙 분리"""
        temp_dir = os.path.join(self.base_dir, 'temp', str(song_request_id))
        temp_file_path = os.path.join(temp_dir, f"temp_{file_number}.mp3")
        
        os.makedirs(temp_dir, exist_ok=True)
        shutil.copy2(input_file_path, temp_file_path)
        
        stages = [
            ('Kim_Vocal_1.onnx', "Kim Vocal 1 separation"),
            ('6_HP-Karaoke-UVR.pth', "6HP-Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb application"),
            ('UVR-DeNoise.pth', "Denoising")
        ]
        
        current_input = temp_file_path
        for model_name, stage_name in stages:
            success = await self.process_stage(current_input, model_name, temp_dir, stage_name)
            if not success:
                raise RuntimeError(f"Failed during {stage_name}")
            
            if stage_name == "Kim Vocal 1 separation":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1.mp3"
            elif stage_name == "6HP-Karaoke separation":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
            elif stage_name == "Reverb application":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
        
        # 최종 결과 파일 복사
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        # 최종 파일들 복사
        shutil.copy2(f"{temp_dir}/temp_{file_number}_(Instrumental)_Kim_Vocal_1.mp3", 
                    result_paths['mr'])
        shutil.copy2(f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3", 
                    result_paths['chorus'])
        shutil.copy2(f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3", 
                    result_paths['vocal'])
        
        return result_paths