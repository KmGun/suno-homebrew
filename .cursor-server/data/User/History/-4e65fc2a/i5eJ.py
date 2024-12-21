import os
import shutil
import asyncio
import subprocess
from typing import Dict

class SubprocessSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
        self.base_params = {
            'output_format': 'mp3',
            'normalization': '0.9',
            'model_file_dir': f'{base_dir}/models'
        }
    
    async def process_stage(self, input_path: str, model_name: str, temp_dir: str, stage_name: str) -> bool:
        """Process a single separation stage using subprocess"""
        print(f"Starting {stage_name} with {model_name}...")
        
        try:
            # Configure command based on model type
            if model_name.endswith('.pth'):  # VR models
                cmd = [
                    "audio-separator",
                    input_path,
                    "-m", model_name,
                    f"--output_dir={temp_dir}",
                    "--output_format=mp3",
                    "--normalization=0.9",
                    "--vr_window_size=320",
                    "--vr_aggression=10"
                ]
            else:  # MDX models (onnx)
                cmd = [
                    "audio-separator",
                    input_path,
                    "-m", model_name,
                    f"--output_dir={temp_dir}",
                    "--output_format=mp3",
                    "--normalization=0.9",
                    "--mdx_segment_size=256",
                    "--mdx_overlap=0.25"
                ]
            
            # Run the command
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print(f"Error in {stage_name}: {stderr.decode()}")
                return False
                
            # Allow time for file system operations to complete
            await asyncio.sleep(1)
            return True
            
        except Exception as e:
            print(f"Error during {stage_name}: {str(e)}")
            return False

    async def separate_audio_tracks(self, input_file_path: str, song_request_id: str, file_number: int) -> Dict[str, str]:
        """Separate audio tracks using subprocess commands"""
        temp_dir = os.path.join(self.base_dir, 'temp', str(song_request_id))
        temp_file_path = os.path.join(temp_dir, f"temp_{file_number}.mp3")
        
        # Ensure temp directory exists
        os.makedirs(temp_dir, exist_ok=True)
        
        # Copy input file
        shutil.copy2(input_file_path, temp_file_path)
        
        # Define processing stages
        stages = [
            ('Kim_Vocal_1.onnx', "Kim Vocal 1 separation"),
            ('6_HP-Karaoke-UVR.pth', "6HP-Karaoke separation"),
            ('Reverb_HQ_By_FoxJoy.onnx', "Reverb application"),
            ('UVR-DeNoise.pth', "Denoising")
        ]
        
        # Process each stage
        current_input = temp_file_path
        file_base = os.path.basename(temp_file_path).replace('.mp3', '')
        
        for model_name, stage_name in stages:
            success = await self.process_stage(current_input, model_name, temp_dir, stage_name)
            if not success:
                raise RuntimeError(f"Failed during {stage_name}")
            
            # Update input path for next stage
            if stage_name == "Kim Vocal 1 separation":
                current_input = f"{temp_dir}/{file_base}_(Vocals)_Kim_Vocal_1.mp3"
            elif stage_name == "6HP-Karaoke separation":
                current_input = f"{temp_dir}/{file_base}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR.mp3"
            elif stage_name == "Reverb application":
                current_input = f"{temp_dir}/{file_base}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy.mp3"
        
        # Define result paths
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        # Copy files to final locations
        shutil.copy2(
            f"{temp_dir}/{file_base}_(Instrumental)_Kim_Vocal_1.mp3", 
            result_paths['mr']
        )
        shutil.copy2(
            f"{temp_dir}/{file_base}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3", 
            result_paths['chorus']
        )
        shutil.copy2(
            f"{temp_dir}/{file_base}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3", 
            result_paths['vocal']
        )
        
        return result_paths