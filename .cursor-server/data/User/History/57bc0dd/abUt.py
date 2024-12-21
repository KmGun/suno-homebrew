import boto3
import logging
import os
from typing import Dict, Any
from src.infer import infer_ai_cover
from pathlib import Path
from dotenv import load_dotenv
from src.post_process_audio import mix_audio

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

class AICoverProcessor:
    def __init__(self):
        # .env 파일 명시적으로 로드
        env_path = Path("/app/.env")
        if env_path.exists():
            load_dotenv(env_path)
            logger.info("Loaded .env file from /app/.env")
        else:
            logger.error(f"No .env file found at {env_path}")
            
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not aws_access_key or not aws_secret_key:
            logger.error("AWS credentials not found in environment variables")
            raise ValueError("AWS credentials not found")
        
        self.s3 = boto3.client(
            "s3",
            region_name="ap-northeast-2",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
        self.bucket_name = "song-request-bucket-1"

    def upload_to_s3(self, local_path: str, s3_path: str):
        """파일을 S3에 업로드합니다."""
        try:
            self.s3.upload_file(local_path, self.bucket_name, s3_path)
            logger.info(f"Uploaded {local_path} to {s3_path}")
        except Exception as e:
            logger.error(f"Failed to upload {local_path}: {e}")
            raise

    def change_pitch_sox(input_filepath, output_filepath, semitones):
        tfm = sox.Transformer()
        tfm.pitch(semitones)
        tfm.build(input_filepath, output_filepath)


    def process_mr_files(input_directory, output_directory, semitones):
        for filename in os.listdir(input_directory):
            if filename.endswith("_mr.mp3"):
                input_filepath = os.path.join(input_directory, filename)
                output_filepath = os.path.join(output_directory, filename)
                if semitones != 0:
                    change_pitch_sox(input_filepath, output_filepath, semitones)
                elif semitones == 0:
                    shutil.copy(input_filepath, output_filepath)

                return output_filepath

        pitch_values_by_model = {
            "ljb": [-1, 0, 1],
            "ssk": [-2, -1, 0],
            # ... (다른 모델들)
        }

    def process_cover(self, guide_path: str, model_name: str, song_request_id: str, index: int) -> bool:
        """AI 커버를 생성하고 S3에 업로드합니다."""
        try:
            # 추론
            reverb_pairs = infer_ai_cover(
                guide_path=guide_path,
                voice_model=model_name,
                song_request_id=song_request_id,
                index=index
            )
            
            example = ['/app/temp/[-1]_reverb.mp3', '/app/temp/[0]_reverb.mp3', '/app/temp/[1]_reverb.mp3']

            # mr 파일 피치 변경
            mr_path = f'/app/temp/{song_request_id}/{index}_mr.mp3'
            
            # 각 리버브 파일에 대해 MR과 믹스
            audioPairs = []
            for reverb_path in reverb_pairs:
                # 믹스된 파일명 생성
                mixed_filename = os.path.basename(reverb_path).replace("reverb", "mixed")
                mixed_path = os.path.join(os.path.dirname(reverb_path), mixed_filename)
                
                # 오디오 믹스 실행
                mix_audio(
                    vocal_path=reverb_path,
                    mr_path=mr_path,
                    output_path=mixed_path
                )
                
                audioPairs.append({
                    'local_path': mixed_path,
                    'file_name': mixed_filename
                })

            # 결과물 S3 업로드
            for pair in audioPairs:
                self.upload_to_s3(
                    pair['local_path'],
                    f"suno-homebrew/{os.path.basename(guide_path)}/{pair['file_name']}"
                )

            return True

        except Exception as e:
            logger.error(f"Error in process_cover: {str(e)}")
            return False
