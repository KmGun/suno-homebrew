import boto3
import logging
import os
from typing import Dict, Any
from infer import infer_ai_cover

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

class AICoverProcessor:
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
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

    def process_cover(self, guide_path: str, model_name: str, is_male: bool) -> bool:
        """AI 커버를 생성하고 S3에 업로드합니다."""
        try:
            # 임시 요청 ID 생성 (실제 구현에서는 적절한 ID 생성 로직 필요)
            request_id = "test_request"
            
            # AI 커버 생성
            result_folder, song_pairs = infer_ai_cover(
                request_id=request_id,
                user_id="test_user",
                song_title="test_song",
                guide_path=guide_path,
                voice_model=model_name,
                is_male=is_male
            )

            # 결과물 S3 업로드
            for pair in song_pairs:
                self.upload_to_s3(
                    pair['local_path'],
                    f"song-requests/{request_id}/{pair['file_name']}"
                )

            return True

        except Exception as e:
            logger.error(f"Error in process_cover: {str(e)}")
            return False
