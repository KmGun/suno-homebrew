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

os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

def clear_gpu_memory():
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
        params = self.base_params.copy()
        params['output_dir'] = temp_dir
        return Separator(**params)

    async def process_stage(self, input_path, model_name, temp_dir, stage_name):
        print(f"\n=== Processing {stage_name} ===")
        print(f"Input path: {input_path}")
        print(f"Model: {model_name}")
        print(f"Temp dir: {temp_dir}")
        
        if not os.path.exists(input_path):
            print(f"ERROR: Input file not found: {input_path}")
            print("Current files in temp dir:")
            for file in os.listdir(temp_dir):
                print(f"  - {file}")
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            clear_gpu_memory()
            separator = self._create_separator(temp_dir)
            separator.load_model(model_filename=model_name)
            separator.separate(input_path)
            
            # 단계별로 생성된 파일 확인
            print(f"\nFiles generated after {stage_name}:")
            for file in os.listdir(temp_dir):
                if file.startswith(f"temp_{os.path.basename(input_path).split('_')[1]}"):
                    print(f"  - {file}")
            
            clear_gpu_memory()
            return True
            
        except RuntimeError as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        temp_dir = os.path.join(self.base_dir, 'temp', str(song_request_id))
        temp_file_path = os.path.join(temp_dir, f"temp_{file_number}.mp3")
        
        print(f"\n=== Starting separation process ===")
        print(f"Input file: {input_file_path}")
        print(f"Temp dir: {temp_dir}")
        print(f"Initial temp file: {temp_file_path}")
        
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
        # Denoising 단계에서 Reverb 결과물 사용
        if stage_name == "Denoising":
            print("\n=== Before Denoising: Checking available files ===")
            print(f"Directory path: {temp_dir}")
            print("Files in directory:")
            for file in sorted(os.listdir(temp_dir)):
                print(f"  - {file}")
                
            # Reverb 단계에서 생성된 파일명 그대로 사용
            current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
            print(f"\nTrying to use file: {current_input}")
            print(f"File exists: {os.path.exists(current_input)}")
            
            if not os.path.exists(current_input):
                raise FileNotFoundError(f"Input file not found: {current_input}")
                
        success = await self.process_stage(current_input, model_name, temp_dir, stage_name)
            if not success:
                raise RuntimeError(f"Failed during {stage_name}")
            
            print(f"\nUpdating input path for next stage after {stage_name}")
            print(f"Previous input: {current_input}")
            
            # 다음 단계 입력 파일 설정
            if stage_name == "Kim Vocal 1 separation":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1.mp3"
            elif stage_name == "6HP-Karaoke separation":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
            elif stage_name == "Reverb application":
                current_input = f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
            
            print(f"New input: {current_input}")
        
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        print("\n=== Copying final results ===")
        print("Source files:")
        source_files = [
            f"{temp_dir}/temp_{file_number}_(Instrumental)_Kim_Vocal_1.mp3",
            f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3",
            f"{temp_dir}/temp_{file_number}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3"
        ]
        for src in source_files:
            print(f"  - {src}")
        
        print("\nDestination files:")
        for key, path in result_paths.items():
            print(f"  - {key}: {path}")
        
        # 최종 파일 복사
        shutil.copy2(source_files[0], result_paths['mr'])
        shutil.copy2(source_files[1], result_paths['chorus'])
        shutil.copy2(source_files[2], result_paths['vocal'])
        
        print("\n=== Final files in temp directory ===")
        for file in os.listdir(temp_dir):
            print(f"  - {file}")
        
        return result_paths