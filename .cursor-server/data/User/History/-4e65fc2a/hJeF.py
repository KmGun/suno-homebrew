class SubprocessBasedSeparator:
    def __init__(self, base_dir):
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

    async def separate_audio_tracks(self, input_file_path, song_request_id, file_number):
        print(f"\n{'='*50}")
        print("=== Starting audio track separation ===")
        print(f"{'='*50}")
        
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
            
            # Denoising stage에서 특별한 처리
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
        
        print("\n--- Creating final output files ---")
        for output_type, source_path in result_paths.items():
            dest_path = os.path.join(temp_dir, f"temp_{identifier}_{output_type}.mp3")
            print(f"\nCopying {output_type}:")
            print(f"  From: {source_path}")
            print(f"  To: {dest_path}")
            shutil.copy2(source_path, dest_path)
            print(f"  Success: {os.path.exists(dest_path)}")
        
        return result_paths