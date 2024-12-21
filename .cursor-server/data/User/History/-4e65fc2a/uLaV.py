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

# CUDA 메모리 관리 설정 개선
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:128,garbage_collection_threshold:0.8,roundup_power2_divisions:32"

def clear_gpu_memory():
    """GPU 메모리를 더 철저하게 정리"""
    gc.collect()
    if torch.cuda.is_available():
        with torch.cuda.device('cuda'):
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            # 메모리 단편화 방지를 위한 추가 대기
            time.sleep(1)

class MemoryEfficientSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
        self.base_params = {
            'output_format': 'mp3',
            'normalization_threshold': 0.9,
            'model_file_dir': f'{base_dir}/models',
            'device_type': 'cuda',
            'batch_size': 1,
            'overlap': 0.05  # 오버랩 감소
        }
        
    def _create_separator(self, temp_dir):
        """메모리 상태에 따른 동적 설정으로 분리기 생성"""
        params = self.base_params.copy()
        params['output_dir'] = temp_dir
        
        if torch.cuda.is_available():
            # 더 정확한 메모리 계산
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated(0)
            cached_memory = torch.cuda.memory_reserved(0)
            free_memory = total_memory - allocated_memory - cached_memory
            
            # 가용 메모리에 따른 배치 크기와 오버랩 동적 조정
            if free_memory < 1 * (1024 ** 3):  # 1GB 미만
                params['batch_size'] = 0.25
                params['overlap'] = 0.01
            elif free_memory < 2 * (1024 ** 3):  # 2GB 미만
                params['batch_size'] = 0.5
                params['overlap'] = 0.02
            elif free_memory < 4 * (1024 ** 3):  # 4GB 미만
                params['batch_size'] = 0.75
                params['overlap'] = 0.03
            else:
                params['batch_size'] = 1
                params['overlap'] = 0.05
            
            # 메모리 상태 로깅
            print(f"Available GPU memory: {free_memory/1024**3:.2f}GB")
            print(f"Selected batch_size: {params['batch_size']}, overlap: {params['overlap']}")
        
        return Separator(**params)

    async def process_stage(self, input_path, model_name, temp_dir, stage_name):
        """메모리 관리가 개선된 단계별 처리"""
        print(f"Starting {stage_name} with {model_name}...")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            clear_gpu_memory()
            separator = self._create_separator(temp_dir)
            
            # 모델 로드 전 추가 메모리 정리
            clear_gpu_memory()
            separator.load_model(model_filename=model_name)
            
            # 분리 작업 전 메모리 상태 확인
            if torch.cuda.is_available():
                print(f"Memory before separation: {torch.cuda.memory_allocated()/1024**3:.2f}GB")
            
            separator.separate(input_path)
            clear_gpu_memory()
            
            # 출력 파일 확인
            expected_files = self._get_expected_output_files(input_path, stage_name)
            for file_path in expected_files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Expected output file not generated: {file_path}")
                print(f"Generated output file: {file_path}")
            
            return True
            
        except RuntimeError as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            if "CUDA out of memory" in str(e):
                try:
                    # 더 극단적인 메모리 절약 모드로 재시도
                    clear_gpu_memory()
                    self.base_params['batch_size'] = 0.25
                    self.base_params['overlap'] = 0.01
                    separator = self._create_separator(temp_dir)
                    separator.load_model(model_filename=model_name)
                    separator.separate(input_path)
                    clear_gpu_memory()
                    return True
                except Exception as retry_error:
                    print(f"Retry failed for {stage_name}: {str(retry_error)}")
                    raise
            raise

    def _get_expected_output_files(self, input_path, stage_name):
        """각 단계별 예상되는 출력 파일 목록 반환"""
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        base_dir = os.path.dirname(input_path)
        
        if stage_name == "Kim Vocal 1 separation":
            return [
                os.path.join(base_dir, f"{base_name}_(Vocals)_Kim_Vocal_1.mp3"),
                os.path.join(base_dir, f"{base_name}_(Instrumental)_Kim_Vocal_1.mp3")
            ]
        elif stage_name == "6HP-Karaoke separation":
            input_name = base_name
            if base_name.endswith("_Kim_Vocal_1"):
                return [
                    os.path.join(base_dir, f"{base_name}_(Vocals)_6_HP-Karaoke-UVR.mp3"),
                    os.path.join(base_dir, f"{base_name}_(Instrumental)_6_HP-Karaoke-UVR.mp3")
                ]
            return [
                os.path.join(base_dir, f"{input_name}_(Vocals)_6_HP-Karaoke-UVR.mp3"),
                os.path.join(base_dir, f"{input_name}_(Instrumental)_6_HP-Karaoke-UVR.mp3")
            ]
        elif stage_name == "Reverb application":
            return [
                os.path.join(base_dir, f"{base_name}_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"),
                os.path.join(base_dir, f"{base_name}_(Reverb)_Reverb_HQ_By_FoxJoy.mp3")
            ]
        elif stage_name == "Denoising":
            # Reverb 단계의 (Instrumental) 출력을 입력으로 사용
            input_base = base_name.replace("_(Reverb)_Reverb_HQ_By_FoxJoy", "_(Instrumental)_Reverb_HQ_By_FoxJoy")
            return [
                os.path.join(base_dir, f"{input_base}_(Instrumental)_UVR-DeNoise.mp3"),
                os.path.join(base_dir, f"{input_base}_(Vocals)_UVR-DeNoise.mp3")
            ]
        return []

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        """메모리 관리가 개선된 오디오 트랙 분리"""
        temp_dir = os.path.join(self.base_dir, 'temp', str(song_request_id))
        temp_file_path = os.path.join(temp_dir, f"temp_{file_number}.mp3")
        
        print(f"Processing in temporary directory: {temp_dir}")
        
        os.makedirs(temp_dir, exist_ok=True)
        shutil.copy2(input_file_path, temp_file_path)
        
        # 각 단계 사이에 메모리 정리 추가
        stages = [
            ('Kim_Vocal_1.onnx', "Kim Vocal 1 separation"),
            ('6_HP-Karaoke-UVR.pth', "6HP-Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb application"),
            ('UVR-DeNoise.pth', "Denoising")
        ]
        
        current_input = temp_file_path
        for model_name, stage_name in stages:
            # 각 스테이지 전에 메모리 정리
            clear_gpu_memory()
            success = await self.process_stage(current_input, model_name, temp_dir, stage_name)
            if not success:
                raise RuntimeError(f"Failed during {stage_name}")
            
            # 출력 파일 패턴에 따라 다음 입력 경로 업데이트
            if stage_name == "Kim Vocal 1 separation":
                current_input = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1.mp3"
            
            # 스테이지 간 추가 메모리 정리
            clear_gpu_memory()
        
        # 결과 파일 복사
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Instrumental)_Kim_Vocal_1.mp3", 
                    result_paths['mr'])
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3", 
                    result_paths['chorus'])
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3", 
                    result_paths['vocal'])
        
        return result_paths