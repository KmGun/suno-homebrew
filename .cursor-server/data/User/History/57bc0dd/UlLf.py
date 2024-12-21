import boto3
import logging
import os
from typing import Dict, Any
from src.infer import infer_ai_cover
from pathlib import Path
from dotenv import load_dotenv
from src.post_process_audio import mix_audio
from src.infer import PITCH_VALUES_BY_MODEL
import shutil
import sox

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

    def change_pitch_sox(self, input_filepath, output_filepath, semitones):
        tfm = sox.Transformer()
        tfm.pitch(semitones)
        tfm.build(input_filepath, output_filepath)

    def process_mr_files(self, input_filepath: str, output_directory: str, semitones: int) -> str:
        """
        MR 파일의 피치를 변경하고 저장합니다.
        
        Args:
            input_filepath: 입력 MR 파일 경로
            output_directory: 출력 디렉토리
            semitones: 변경할 피치값
        
        Returns:
            생성된 파일의 경로
        """
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(output_directory, f"[{semitones}]{filename}")
        
        if semitones != 0:
            self.change_pitch_sox(input_filepath, output_filepath, semitones)
        else:
            shutil.copy(input_filepath, output_filepath)
        
        return output_filepath

    def process_cover(self, guide_path: str, model_name: str, song_request_id: str, index: int) -> list:
        """AI 커버를 생성하고 S3에 업로드합니다."""
        try:
            # 결과 디렉토리 생성
            output_directory = f'/app/temp/{song_request_id}'
            os.makedirs(output_directory, exist_ok=True)
            
            # 추론
            reverb_pairs = infer_ai_cover(
                guide_path=guide_path,
                voice_model=model_name,
                song_request_id=song_request_id,
                index=index
            )
            
            if not reverb_pairs:
                logger.error("No reverb files generated")
                return []

            # mr 파일 피치 변경
            mr_path = f'/app/temp/{song_request_id}/{index}_mr.mp3'
            if not os.path.exists(mr_path):
                logger.error(f"MR file not found: {mr_path}")
                return []
            
            mr_files = []
            for pitch in PITCH_VALUES_BY_MODEL[model_name]:
                pitched_mr = self.process_mr_files(
                    input_filepath=mr_path,
                    output_directory=output_directory,
                    semitones=pitch
                )
                mr_files.append(pitched_mr)

            result_urls = []
            # 각 리버브 파일과 해당하는 피치의 MR 파일을 매칭하여 믹스
            for reverb_path, mr_file in zip(reverb_pairs, mr_files):
                if not os.path.exists(reverb_path):
                    logger.error(f"Reverb file not found: {reverb_path}")
                    continue
                
                pitch_prefix = os.path.basename(reverb_path).split(']')[0] + ']'
                result_filename = f"{pitch_prefix}{index}_result.mp3"
                result_path = os.path.join(output_directory, result_filename)
                
                # 오디오 믹스 실행
                mix_audio(
                    vocal_path=reverb_path,
                    mr_path=mr_file,
                    output_path=result_path
                )
                
                # S3에 업로드하고 URL 저장
                s3_path = f"song-requests/{song_request_id}/{result_filename}"
                self.upload_to_s3(result_path, s3_path)
                
                # S3 URL 형식으로 변환
                s3_url = f"https://{self.bucket_name}.s3.ap-northeast-2.amazonaws.com/{s3_path}"
                result_urls.append(s3_url)

            return result_urls

        except Exception as e:
            logger.error(f"Error in process_cover: {str(e)}")
            return []
