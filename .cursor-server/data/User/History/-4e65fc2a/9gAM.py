import os
import shutil
import gc
import torch
import subprocess
import time

def clear_gpu_memory():
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
                'instrumental': f"{base_name}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3"
            }
        }
        
        patterns = filename_patterns[model_name]
        print("Generated filename patterns:")
        for key, value in patterns.items():
            print(f"  - {key}: {value}")
        return patterns

    async def process_stage(self, input_path, model_name, temp_dir, stage_name, identifier):
        print(f"\n{'='*50}")
        print(f"=== Starting {stage_name} stage ===")
        print(f"{'='*50}")
        print(f"Input path: {input_path}")
        print(f"Model: {model_name}")
        print(f"Temp directory: {temp_dir}")
        print(f"Identifier: {identifier}")
        
        # Check input file
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
            
            cmd = ["audio-separator", input_path, "-m", model_name, 
                  "--output_dir", temp_dir, "--output_format=mp3",
                  "--normalization=0.9"]
            
            if model_name.endswith('.onnx'):
                print("Adding ONNX model parameters")
                cmd.extend(["--mdx_segment_size=256", "--mdx_overlap=0.25"])
            else:
                print("Adding PTH model parameters")
                cmd.extend(["--vr_window_size=320", "--vr_aggression=10"])
            
            print("Final command:")
            print(" ".join(cmd))
            
            print("\n--- Executing command ---")
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            print("Command output:")
            print(process.stdout)
            
            if process.stderr:
                print("Command stderr:")
                print(process.stderr)
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed with return code {process.returncode}")
            
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
        print(f"\n{'='*50}")
        print("=== Starting audio track separation ===")
        print(f"{'='*50}")
        print(f"Input file: {input_file_path}")
        print(f"Song request ID: {song_request_id}")
        print(f"File number: {file_number}")
        
        identifier = file_number
        temp_dir = os.path.join(self.base_dir, 'temp', song_request_id)
        temp_file_path = f"{temp_dir}/temp_{identifier}.mp3"
        
        print(f"\n--- Setting up temporary directory ---")
        print(f"Temp directory: {temp_dir}")
        os.makedirs(temp_dir, exist_ok=True)
        print(f"Copying input file to: {temp_file_path}")
        shutil.copy2(input_file_path, temp_file_path)
        
        stages = [
            ('Kim_Vocal_1.onnx', "Vocal separation"),
            ('6_HP-Karaoke-UVR.pth', "Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb processing"),
            ('UVR-DeNoise.pth', "Noise reduction")
        ]
        
        current_input = temp_file_path
        stage_outputs = {}
        
        print("\n--- Processing stages ---")
        for model_name, stage_name in stages:
            print(f"\nStarting stage: {stage_name}")
            print(f"Using model: {model_name}")
            print(f"Current input: {current_input}")
            
            if stage_name == "Noise reduction":
                print("\n--- Preparing for Noise reduction ---")
                current_input = os.path.join(temp_dir, stage_outputs['Reverb processing']['main'])
                print(f"Updated input for noise reduction: {current_input}")
                print(f"File exists: {os.path.exists(current_input)}")
            
            output_files = await self.process_stage(current_input, model_name, temp_dir, 
                                                  stage_name, identifier)
            stage_outputs[stage_name] = output_files
            
            if stage_name != "Noise reduction":
                if 'vocals' in output_files:
                    current_input = os.path.join(temp_dir, output_files['vocals'])
                    print(f"Updated input for next stage: {current_input}")
        
        print("\n--- Preparing final results ---")
        result_paths = {
            'mr': os.path.join(temp_dir, stage_outputs['Vocal separation']['instrumental']),
            'chorus': os.path.join(temp_dir, stage_outputs['Karaoke separation']['instrumental']),
            'vocal': os.path.join(temp_dir, stage_outputs['Noise reduction']['instrumental'])
        }
        
        print("\nFinal output paths:")
        for output_type, path in result_paths.items():
            print(f"  - {output_type}: {path}")
            print(f"    Exists: {os.path.exists(path)}")
            if os.path.exists(path):
                print(f"    Size: {os.path.getsize(path)} bytes")
        
        print("\n--- Creating final output files ---")
        for output_type, source_path in result_paths.items():
            dest_path = os.path.join(temp_dir, f"temp_{identifier}_{output_type}.mp3")
            print(f"\nCopying {output_type}:")
            print(f"  From: {source_path}")
            print(f"  To: {dest_path}")
            shutil.copy2(source_path, dest_path)
            print(f"  Success: {os.path.exists(dest_path)}")
        
        print("\n=== Final files in temp directory ===")
        for file in sorted(os.listdir(temp_dir)):
            print(f"  - {file}")
        
        return result_paths