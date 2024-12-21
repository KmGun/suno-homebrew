import os
import shutil
import gc
import torch
import subprocess
import time

def clear_gpu_memory():
    """Clear GPU memory to prevent memory leaks"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()

class SubprocessBasedSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
    
    def get_output_filename(self, base_name, stage, model_name):
        """Generate correct output filename based on processing stage"""
        print(f"\n=== Generating filename patterns for {stage} ===")
        print(f"Base name: {base_name}")
        print(f"Model: {model_name}")
        
        filename_patterns = {
            'Kim_Vocal_1.onnx': {
                'vocals': f"{base_name}_(Vocals)_Kim_Vocal_1.mp3",
                'instrumental': f"{base_name}_(Instrumental)_Kim_Vocal_1.mp3"
            },
            '6_HP-Karaoke-UVR.pth': {
                'vocals': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3",
                'instrumental': f"{base_name}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3"
            },
            'Reverb_HQ_By_FoxJoy.onnx': {
                'main': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3",
                'reverb': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Reverb)_Reverb_HQ_By_FoxJoy.mp3"
            },
            'UVR-DeNoise.pth': {
                'input': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3",
                'instrumental': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3"
            }
        }
        
        patterns = filename_patterns[model_name]
        print("Generated filename patterns:")
        for key, value in patterns.items():
            print(f"  - {key}: {value}")
        return patterns

    async def process_stage(self, input_path, model_name, temp_dir, stage_name, identifier):
        """Process a single stage of audio separation"""
        print(f"\n{'='*50}")
        print(f"=== Starting {stage_name} stage ===")
        print(f"{'='*50}")
        print(f"Input path: {input_path}")
        print(f"Model: {model_name}")
        print(f"Temp directory: {temp_dir}")
        print(f"Identifier: {identifier}")
        
        # Verify input file exists
        print(f"\n--- Checking input file ---")
        if not os.path.exists(input_path):
            print(f"ERROR: Input file not found: {input_path}")
            print("\nCurrent files in temp directory:")
            for file in sorted(os.listdir(temp_dir)):
                print(f"  - {file}")
            raise FileNotFoundError(f"Input file not found: {input_path}")
        else:
            print(f"Input file exists: {input_path}")
            print(f"File size: {os.path.getsize(input_path)} bytes")
        
        try:
            clear_gpu_memory()
            print("\n--- Building command ---")
            
            # Prepare audio-separator command
            cmd = ["audio-separator", input_path, "-m", model_name, 
                  "--output_dir", temp_dir, "--output_format=mp3",
                  "--normalization=0.9"]
            
            # Add model-specific parameters
            if model_name.endswith('.onnx'):
                print("Adding ONNX model parameters")
                cmd.extend(["--mdx_segment_size=256", "--mdx_overlap=0.25"])
            else:
                print("Adding PTH model parameters")
                cmd.extend(["--vr_window_size=320", "--vr_aggression=10"])
            
            print("Final command:")
            print(" ".join(cmd))
            
            # Execute command
            print("\n--- Executing command ---")
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("Command output:")
            print(process.stdout)
            
            if process.stderr:
                print("Command stderr:")
                print(process.stderr)
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed with return code {process.returncode}")
            
            # Verify output files
            print("\n--- Checking output files ---")
            base_name = f"temp_{identifier}"
            expected_files = self.get_output_filename(base_name, stage_name, model_name)
            
            print("\nVerifying expected output files:")
            for output_type, filename in expected_files.items():
                full_path = os.path.join(temp_dir, filename)
                print(f"\nChecking {output_type} file:")
                print(f"  Path: {full_path}")
                if os.path.exists(full_path):
                    print(f"  Status: Found")
                    print(f"  Size: {os.path.getsize(full_path)} bytes")
                else:
                    print(f"  Status: NOT FOUND")
                    print("\nCurrent files in directory:")
                    for file in sorted(os.listdir(temp_dir)):
                        print(f"  - {file}")
                    raise FileNotFoundError(f"Expected output file not found: {filename}")
            
            clear_gpu_memory()
            time.sleep(2)
            return expected_files
            
        except Exception as e:
            clear_gpu_memory()
            print(f"\n{'!'*50}")
            print(f"ERROR during {stage_name}: {str(e)}")
            print(f"{'!'*50}")
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        """Main method to process audio separation with all stages"""
        print(f"\n{'='*50}")
        print("=== Starting audio track separation ===")
        print(f"{'='*50}")
        print(f"Input file: {input_file_path}")
        print(f"Song request ID: {song_request_id}")
        print(f"File number: {file_number}")
        
        identifier = file_number
        temp_dir = os.path.join(self.base_dir, 'temp', song_request_id)
        temp_file_path = f"{temp_dir}/temp_{identifier}.mp3"
        
        # Setup temporary directory
        print(f"\n--- Setting up temporary directory ---")
        print(f"Temp directory: {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)
        
        print(f"Copying input file to: {temp_file_path}")
        shutil.copy2(input_file_path, temp_file_path)
        
        # Define processing stages
        stages = [
            ('Kim_Vocal_1.onnx', "Vocal separation"),
            ('6_HP-Karaoke-UVR.pth', "Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb processing"),
            ('UVR-DeNoise.pth', "Noise reduction")
        ]
        
        current_input = temp_file_path
        stage_outputs = {}
        
        # Process each stage
        print("\n--- Processing stages ---")
        for model_name, stage_name in stages:
            print(f"\nStarting stage: {stage_name}")
            print(f"Using model: {model_name}")
            print(f"Current input: {current_input}")
            
            # Special handling for Denoising stage
            if stage_name == "Noise reduction":
                print("\n--- Preparing for Noise reduction ---")
                expected_files = self.get_output_filename(f"temp_{identifier}", stage_name, model_name)
                current_input = os.path.join(temp_dir, expected_files['input'])
                print(f"Updated input for noise reduction: {current_input}")
                print(f"File exists: {os.path.exists(current_input)}")
                
                if not os.path.exists(current_input):
                    print("\nListing all files in temp directory:")
                    for file in sorted(os.listdir(temp_dir)):
                        print(f"  - {file}")
                    raise FileNotFoundError(f"Input file not found: {current_input}")
            
            output_files = await self.process_stage(current_input, model_name, temp_dir, 
                                                  stage_name, identifier)
            stage_outputs[stage_name] = output_files
            
            # Update input for next stage
            if stage_name != "Noise reduction":
                if 'vocals' in output_files:
                    current_input = os.path.join(temp_dir, output_files['vocals'])
                    print(f"Updated input for next stage: {current_input}")
        
        # Prepare final results
        print("\n--- 최종 결과 파일 생성 중 ---")
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        # 최종 파일 복사 및 이름 변경
        for output_type, dest_path in result_paths.items():
            source_path = os.path.join(temp_dir, stage_outputs['Noise reduction']['instrumental'])
            if output_type == 'mr':
                source_path = os.path.join(temp_dir, stage_outputs['Vocal separation']['instrumental'])
            elif output_type == 'chorus':
                source_path = os.path.join(temp_dir, stage_outputs['Karaoke separation']['instrumental'])
            
            print(f"\n{output_type} 파일 복사 중:")
            print(f"  원본: {source_path}")
            print(f"  대상: {dest_path}")
            shutil.copy2(source_path, dest_path)
            print(f"  성공: {os.path.exists(dest_path)}")
        
        # temp 파일 정리
        print("\n--- 임시 파일 정리 중 ---")
        for file in os.listdir(temp_dir):
            if 'temp_' in file:
                file_path = os.path.join(temp_dir, file)
                try:
                    os.remove(file_path)
                    print(f"삭제됨: {file}")
                except Exception as e:
                    print(f"파일 삭제 실패 {file}: {str(e)}")
        
        return result_paths