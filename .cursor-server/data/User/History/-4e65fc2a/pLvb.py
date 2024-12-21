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

# Set PyTorch memory management settings
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True,max_split_size_mb:512"

def clear_gpu_memory():
    """Thoroughly clear GPU memory and wait for operations to complete"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()
        time.sleep(2)

class MemoryEfficientSeparator:
    def __init__(self, base_dir='/app'):
        self.base_dir = base_dir
        self.base_params = {
            'output_format': 'mp3',
            'normalization_threshold': 0.9,
            'model_file_dir': f'{base_dir}/models',
            'device_type': 'cuda',
            'batch_size': 1,
            'overlap': 0.1  # Reduced overlap to save memory
        }
        
    def _create_separator(self, temp_dir):
        """Create a new separator instance with current memory settings"""
        params = self.base_params.copy()
        params['output_dir'] = temp_dir
        
        # Get available GPU memory
        if torch.cuda.is_available():
            free_memory = torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated(0)
            # Adjust batch size based on available memory
            if free_memory < 2 * (1024 ** 3):  # Less than 2GB free
                params['batch_size'] = 1
                params['overlap'] = 0.05
            elif free_memory < 4 * (1024 ** 3):  # Less than 4GB free
                params['batch_size'] = 1
                params['overlap'] = 0.1
        
        return Separator(**params)

    async def process_stage(self, input_path, model_name, temp_dir, stage_name):
        """Process a single separation stage with memory management"""
        print(f"Starting {stage_name} with {model_name}...")
        
        try:
            clear_gpu_memory()
            separator = self._create_separator(temp_dir)
            separator.load_model(model_filename=model_name)
            separator.separate(input_path)
            clear_gpu_memory()
            
            # Allow time for memory to settle
            await asyncio.sleep(1)
            
            return True
            
        except RuntimeError as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            if "CUDA out of memory" in str(e):
                # Try one more time with minimal memory settings
                try:
                    clear_gpu_memory()
                    self.base_params['batch_size'] = 1
                    self.base_params['overlap'] = 0.05
                    separator = self._create_separator(temp_dir)
                    separator.load_model(model_filename=model_name)
                    separator.separate(input_path)
                    clear_gpu_memory()
                    return True
                except Exception as retry_error:
                    print(f"Retry failed for {stage_name}: {str(retry_error)}")
                    raise
            raise

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        """Separate audio tracks with improved memory management"""
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
        
        current_input = temp_file_path
        for model_name, stage_name in stages:
            success = await self.process_stage(current_input, model_name, temp_dir, stage_name)
            if not success:
                raise RuntimeError(f"Failed during {stage_name}")
            
            # Update input path for next stage based on output naming pattern
            # You'll need to modify this based on your actual output file naming convention
            if stage_name == "Kim Vocal 1 separation":
                current_input = f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1.mp3"
            # Add similar patterns for other stages
        
        # Copy final results with simplified names
        result_paths = {
            'mr': os.path.join(temp_dir, f"{file_number}_mr.mp3"),
            'chorus': os.path.join(temp_dir, f"{file_number}_chorus.mp3"),
            'vocal': os.path.join(temp_dir, f"{file_number}_vocal.mp3")
        }
        
        # Copy files to final locations with proper names
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Instrumental)_Kim_Vocal_1.mp3", 
                    result_paths['mr'])
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3", 
                    result_paths['chorus'])
        shutil.copy2(f"{temp_dir}/{os.path.basename(temp_file_path).replace('.mp3', '')}_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(No Reverb)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3", 
                    result_paths['vocal'])
        
        return result_paths