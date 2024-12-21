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
        return filename_patterns[model_name]

    async def process_stage(self, input_path, model_name, temp_dir, stage_name, identifier):
        print(f"\n=== Processing {stage_name} ===")
        
        try:
            clear_gpu_memory()
            
            cmd = ["audio-separator", input_path, "-m", model_name, 
                  "--output_dir", temp_dir, "--output_format=mp3",
                  "--normalization=0.9"]
            
            if model_name.endswith('.onnx'):
                cmd.extend(["--mdx_segment_size=256", "--mdx_overlap=0.25"])
            else:
                cmd.extend(["--vr_window_size=320", "--vr_aggression=10"])
            
            process = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed with return code {process.returncode}")
            
            base_name = f"temp_{identifier}"
            expected_files = self.get_output_filename(base_name, stage_name, model_name)
            
            # Verify output files exist
            for output_type, filename in expected_files.items():
                full_path = os.path.join(temp_dir, filename)
                if not os.path.exists(full_path):
                    raise FileNotFoundError(f"Expected output file not found: {filename}")
            
            clear_gpu_memory()
            time.sleep(2)
            return expected_files
            
        except Exception as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        identifier = file_number
        temp_dir = os.path.join(self.base_dir, 'temp', song_request_id)
        temp_file_path = f"{temp_dir}/temp_{identifier}.mp3"
        
        os.makedirs(temp_dir, exist_ok=True)
        shutil.copy2(input_file_path, temp_file_path)
        
        stages = [
            ('Kim_Vocal_1.onnx', "Vocal separation"),
            ('6_HP-Karaoke-UVR.pth', "Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb processing"),
            ('UVR-DeNoise.pth', "Noise reduction")
        ]
        
        current_input = temp_file_path
        stage_outputs = {}
        
        for model_name, stage_name in stages:
            if stage_name == "Noise reduction":
                # Use the main output from Reverb stage
                current_input = os.path.join(temp_dir, stage_outputs['Reverb processing']['main'])
            
            output_files = await self.process_stage(current_input, model_name, temp_dir, 
                                                  stage_name, identifier)
            stage_outputs[stage_name] = output_files
            
            if stage_name != "Noise reduction":
                # Update input for next stage - use vocals output
                if 'vocals' in output_files:
                    current_input = os.path.join(temp_dir, output_files['vocals'])
        
        # Prepare final results
        result_paths = {
            'mr': os.path.join(temp_dir, stage_outputs['Vocal separation']['instrumental']),
            'chorus': os.path.join(temp_dir, stage_outputs['Karaoke separation']['instrumental']),
            'vocal': os.path.join(temp_dir, stage_outputs['Noise reduction']['instrumental'])
        }
        
        # Create final output files
        for output_type, source_path in result_paths.items():
            dest_path = os.path.join(temp_dir, f"temp_{identifier}_{output_type}.mp3")
            shutil.copy2(source_path, dest_path)
        
        return result_paths