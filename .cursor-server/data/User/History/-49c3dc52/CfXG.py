from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Dict
from uvr import separate_audio_tracks
from src.execute import AICoverProcessor
from suno import generate_audio
from tools import generate_random_identifier, download_mp3
import logging

app = FastAPI()

# CORS 미들웨어 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 구체적인 도메인을 지정하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: Dict[str, WebSocket] = {}

# 로깅 설정 추가
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def process_single_audio(websocket: WebSocket, audio_url: str, song_request_id: str, index: int, model_name: str):
    # 각각의 오디오에 대한 전체 프로세스를 처리하는 함수
    local_file_path = await download_mp3(audio_url, song_request_id, index)
    separated_result = await separate_audio_tracks(local_file_path, song_request_id, index)
    
    aicover_processor = AICoverProcessor()
    result_path = await aicover_processor.process_cover(
        guide_path=separated_result['vocal'],
        model_name=model_name,
        song_request_id=song_request_id,
        index=index
    )
    
    return result_path

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("웹소켓 엔드포인트 진입")  # print로 먼저 테스트
    try:
        await websocket.accept()
        print("연결 수락됨")
        
        while True:  # 연속적인 메시지 수신을 위한 루프
            try:
                data = await websocket.receive_text()  # receive_json() 대신 receive_text() 사용
                print(f"받은 데이터: {data}")
                
                # 응답 보내기
                await websocket.send_json({"status": "received", "message": "메시지를 받았습니다"})
                
            except Exception as e:
                print(f"에러 발생: {str(e)}")
                break
                
    except Exception as e:
        print(f"연결 에러: {str(e)}")
    finally:
        print("연결 종료")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)