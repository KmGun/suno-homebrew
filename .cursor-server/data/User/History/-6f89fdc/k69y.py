# infer.py
import io
import os
import sys
import re
import json
import sox
import shutil
import logging
import boto3


from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from botocore.exceptions import NoCredentialsError
from src.main import voice_change
from src.post_process_audio import apply_reverb
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    aws_access_key_id="YOUR_ACCESS_KEY",
    aws_secret_access_key="YOUR_SECRET_KEY",
    region_name="ap-northeast-2",
)


def process_guide_folders(guide_folders, root_folder):
    # 숫자 prefix로 정렬
    sorted_folders = sorted(guide_folders, key=lambda x: int(x.split("_")[0]))

    # 각 폴더에 대해 full path 생성
    result_paths = [
        f"{root_folder}/{folder}/{folder}_vocal.mp3" for folder in sorted_folders
    ]

    return result_paths


# 파일 경로에서 1_,2_ 를 추출하는 함수
def extract_number(file_path):
    # 파일명 추출
    file_name = os.path.basename(file_path)
    # 파일명에서 숫자 추출
    match = re.match(r"(\d+)_", file_name)
    return int(match.group(1)) if match else float("inf")


def connect_to_google_drive():
    # 인증 정보 JSON 파일 경로
    credentials_path = "/app/homebrew-prod-1aeee50b74d5.json"
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=credentials)
    return service


# def download_file(service, file_id, destination):
#     request = service.files().get_media(fileId=file_id)
#     with open(destination, "wb") as f:
#         downloader = MediaIoBaseDownload(f, request)
#         done = False
#         while not done:
#             status, done = downloader.next_chunk()
#             print("Download progress: %d%%" % int(status.progress() * 100))


def download_folder_by_folder_id(service, folder_id, destination_folder):
    # 폴더의 모든 파일 목록을 가져옵니다.
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query).execute()
    items = results.get("files", [])

    if not items:
        print("No files found in the folder.")
    else:
        # print(f"Found {len(items)} files in the folder:")
        for item in items:
            # print(f" - {item['name']} ({item['id']})")
            file_destination = os.path.join(destination_folder, item["name"])
            download_file(service, item["id"], file_destination)


def download_google_drive_folder(service, folder_id, local_path, folder_name=None):
    """
    Google Drive의 특정 폴더를 로컬에 다운로드합니다.

    Args:
        service: Google Drive API 서비스 객체
        folder_id (str): Google Drive 폴더 ID
        local_path (str): 다운로드할 로컬 경로
        folder_name (str, optional): 다운로드할 특정 하위 폴더 이름. 지정 시 해당 폴더를 찾아 폴더 구조대로 다운로드
    """

    def download_file(file_metadata, path):
        """개별 파일을 다운로드합니다."""
        file_id = file_metadata["id"]
        file_name = file_metadata["name"]
        file_path = os.path.join(path, file_name)

        if "google-apps" in file_metadata["mimeType"]:
            return

        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        try:
            done = False
            while not done:
                status, done = downloader.next_chunk()

            fh.seek(0)
            with open(file_path, "wb") as f:
                f.write(fh.read())

        except Exception as e:
            print(f"Error downloading {file_name}: {str(e)}")

    def find_specific_folder(parent_folder_id, target_folder_name):
        """특정 이름의 하위 폴더를 찾습니다."""
        query = f"'{parent_folder_id}' in parents and name = '{target_folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = (
            service.files()
            .list(q=query, fields="files(id, name)", pageSize=1)
            .execute()
        )

        items = results.get("files", [])
        return items[0] if items else None

    def process_folder(folder_id, current_path):
        """폴더 내의 모든 파일과 하위 폴더를 재귀적으로 처리합니다."""
        # print(f"\nProcessing folder: {folder_id}")
        # print(f"Local path: {current_path}")

        if not os.path.exists(current_path):
            os.makedirs(current_path)
            # print(f"Created directory: {current_path}")

        try:
            # trashed = false 조건 추가하고 파일 정렬
            query = f"'{folder_id}' in parents and trashed = false"
            # print(f"Executing query: {query}")

            results = (
                service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageSize=1000,
                    orderBy="folder,name",
                )
                .execute()
            )

            items = results.get("files", [])
            # print(f"Found {len(items)} items in folder")

            if not items:
                # print("No files found in this folder.")
                return

            for item in items:
                # print(f"\nProcessing item: {item['name']} ({item['mimeType']})")

                if item["mimeType"] == "application/vnd.google-apps.folder":
                    new_folder_path = os.path.join(current_path, item["name"])
                    # print(f"Found subfolder: {item['name']}")
                    process_folder(item["id"], new_folder_path)
                else:
                    download_file(item, current_path)

        except Exception as e:
            print(f"Error processing folder {folder_id}: {str(e)}")

    # print(f"Starting download process")

    if folder_name:
        # print(f"Searching for specific folder: {folder_name}")
        folder_info = find_specific_folder(folder_id, folder_name)

        if folder_info:
            # print(f"Found folder '{folder_name}'. Starting download...")
            # 상위 폴더 생성하고 그 안에 target 폴더 생성
            target_path = os.path.join(local_path, folder_name)
            process_folder(folder_info["id"], target_path)
        else:
            print(
                f"Error: Folder '{folder_name}' not found in the specified parent folder"
            )
            return
    else:
        # print(f"Downloading entire folder {folder_id} to {local_path}")
        process_folder(folder_id, local_path)

    # print("Download process completed")


def check_audio_samplerate(file_path, location_msg):
    """
    [DEBUG] 오디오 파일의 샘플레이트를 체크하는 함수
    나중에 삭제 예정
    """
    try:
        tfm = sox.Transformer()
        sample_rate = tfm.stat(file_path).sample_rate
        logger.info(f"[DEBUG_SAMPLERATE] {location_msg} - File: {file_path}, Sample Rate: {sample_rate}Hz")
    except Exception as e:
        logger.error(f"[DEBUG_SAMPLERATE] Error checking sample rate for {file_path}: {str(e)}")


# 전역 변수로 이동
PITCH_VALUES_BY_MODEL = {
    "ljb": [-1, 0, 1],
    "ssk": [-2, -1, 0],
    # ... (다른 모델들)
}

def infer_ai_cover(guide_path, voice_model, song_request_id, index):
    logger.info(f"Starting inference with parameters: guide_path={guide_path}, voice_model={voice_model}")

    try:
        # 모델 경로 설정
        model_path = f"/app/rvc_models/{voice_model}"
        logger.info(f"모델 경로: {model_path}")

        # 전역 변수 사용
        if voice_model in PITCH_VALUES_BY_MODEL:
            model_pitch_values = PITCH_VALUES_BY_MODEL[voice_model]
        else:
            model_pitch_values = [0]

        reverb_pairs = []
        result_folder = os.path.join("/app/temp", song_request_id)
        os.makedirs(result_folder, exist_ok=True)

        # 추론 시작
        for pitch_value in model_pitch_values:
            output_path = os.path.join(result_folder, f"[{pitch_value}]aivocal{index}.mp3")
            try:
                voice_change(
                    voice_model,
                    guide_path,
                    output_path,
                    pitch_value,
                    f0_method="rmvpe",
                    index_rate=0.66,
                    filter_radius=3,
                    rms_mix_rate=0.25,
                    protect=0.33,
                    crepe_hop_length=128,
                    is_webui=0,
                )

            except Exception as e:
                logger.error(f"추론 중 에러 발생: {str(e)}")
                raise

            # 리버브 적용
            reverb_path = apply_reverb(result_folder, f"[{pitch_value}]reverb{index}.mp3")
            reverb_pairs.append(reverb_path)

        logger.info(f"추론 완료: {voice_model}")
        return reverb_pairs

    except Exception as e:
        logger.error(f"Error in infer_ai_cover: {str(e)}")
        raise
