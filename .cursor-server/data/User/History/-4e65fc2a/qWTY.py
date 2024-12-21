async def process_stage(self, input_path, model_name, temp_dir, stage_name):
        """단계별 처리"""
        print(f"\n=== Processing {stage_name} ===")
        print(f"Input path: {input_path}")
        print(f"Temp dir: {temp_dir}")
        
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        try:
            clear_gpu_memory()
            separator = self._create_separator(temp_dir)
            separator.load_model(model_filename=model_name)
            separator.separate(input_path)
            clear_gpu_memory()
            
            # Reverb 단계 직후 디렉토리 내용 확인
            if stage_name == "Reverb application":
                print("\n=== Files after Reverb stage ===")
                print("Current files in directory:")
                for file in sorted(os.listdir(temp_dir)):
                    print(f"  - {file}")
                    print(f"    Size: {os.path.getsize(os.path.join(temp_dir, file))} bytes")
                    print(f"    Path exists: {os.path.exists(os.path.join(temp_dir, file))}")
            
            return True
            
        except RuntimeError as e:
            clear_gpu_memory()
            print(f"Error during {stage_name}: {str(e)}")
            raise