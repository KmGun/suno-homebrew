from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Dict
from uvr import separate_audio_tracks
from src.execute import AICoverProcessor
from suno import generate_audio
from tools import generate_random_identifier, download_mp3

app = FastAPI()
active_connections: Dict[str, WebSocket] = {}

class SongRequest(BaseModel):
    modelName: str
    lyric: str
    title: str
    style: str
    style_negative: str

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
    print("웹소켓 엔드포인트 진입")  # 추가된 로그
    try:
        print("연결 시도 중...")  # 추가된 로그
        await websocket.accept()
        song_request_id = None
        
        print("웹소켓 연결 수락됨")
        
        # 연결 후 클라이언트로부터 메시지를 기다림
        print("클라이언트로부터 메시지 대기 중...")  # 추가된 로그
        raw_data = await websocket.receive_json()
        print(f"수신된 데이터: {raw_data}")
        
        data = SongRequest(**raw_data)  # Pydantic 모델로 검증
        print("데이터 검증 완료")  # 로깅 추가
        
        # 요청 ID 생성 및 연결 저장
        song_request_id = generate_random_identifier()
        active_connections[song_request_id] = websocket
        
        # 접수 완료 응답
        await websocket.send_json({
            "status": "accepted",
            "songRequestId": song_request_id,
            "message": "신청곡이 접수되었습니다."
        })
        
        # suno original audio 생성
        await websocket.send_json({"status": "generating original audio"})
        result = await generate_audio(data.lyric, data.title, data.style, data.style_negative)
        await websocket.send_json({"status": "processing audio tracks"})

        # 각 오디오 트랙을 독립적인 태스크로 생성
        task1 = asyncio.create_task(
            process_single_audio(
                websocket, 
                result.data[0]["audio_url"], 
                song_request_id, 
                1, 
                data.modelName
            )
        )
        task2 = asyncio.create_task(
            process_single_audio(
                websocket, 
                result.data[1]["audio_url"], 
                song_request_id, 
                2, 
                data.modelName
            )
        )

        # 각 태스크가 완료될 때마다 결과 전송
        for completed_task in asyncio.as_completed([task1, task2]):
            result_path = await completed_task
            await websocket.send_json({
                "status": "track_completed",
                "resultUrl": result_path
            })
        
        # 모든 처리가 완료됨을 알림
        await websocket.send_json({
            "status": "all_completed"
        })
            
    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        if song_request_id and song_request_id in active_connections:
            del active_connections[song_request_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)