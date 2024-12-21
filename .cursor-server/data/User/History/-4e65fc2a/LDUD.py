import os
import shutil
import random
import string
import subprocess
import time
import gc
import torch

def clear_gpu_memory():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

class SubprocessBasedSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
    
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
            
            # Build the command based on model type
            cmd = ["audio-separator", input_path, "-m", model_name, 
                  "--output_dir=/content/temp/", "--output_format=mp3",
                  "--normalization=0.9"]
            
            # Add model-specific parameters
            if model_name.endswith('.onnx'):
                cmd.extend(["--mdx_segment_size=256", "--mdx_overlap=0.25"])
            else:  # .pth models
                cmd.extend(["--vr_window_size=320", "--vr_aggression=10"])
            
            # Execute the command
            process = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                print(f"Error output: {process.stderr}")
                raise RuntimeError(f"Command failed with return code {process.returncode}")
            
            # 단계별로 생성된 파일 확인
            print(f"\nFiles generated after {stage_name}:")
            for file in os.listdir(temp_dir):
                if file.startswith(f"temp_{os.path.basename(input_path).split('_')[1]}"):
                    print(f"  - {file}")
            
            clear_gpu_memory()
            time.sleep(2)  # Add small delay between stages
            return True
            
        except subprocess.CalledProcessError as e:
            clear_gpu_memory()
            print(f"Subprocess error during {stage_name}: {str(e)}")
            print(f"Error output: {e.stderr}")
            raise
        except Exception as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        identifier = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        temp_dir = "/content/temp"
        temp_file_path = f"{temp_dir}/{identifier}.mp3"
        
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
                current_input = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
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
                current_input = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1.mp3"
            elif stage_name == "6HP-Karaoke separation":
                current_input = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
            elif stage_name == "Reverb application":
                current_input = f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
            
            print(f"New input: {current_input}")
        
        result_paths = {
            'mr': os.path.join(temp_dir, f"{identifier}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{identifier}_corus.mp3"),
            'vocal': os.path.join(temp_dir, f"{identifier}_vocal.mp3")
        }
        
        print("\n=== Copying final results ===")
        print("Source files:")
        source_files = [
            f"{temp_dir}/{identifier}_(Instrumental)_Kim_Vocal_1.mp3",
            f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3",
            f"{temp_dir}/{identifier}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3"
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