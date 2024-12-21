from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Dict
from uvr import separate_audio_tracks
from src.execute import AICoverProcessor
from suno import generate_audio
from tools import generate_random_identifier, download_mp3
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
active_connections: Dict[str, WebSocket] = {}

async def process_single_audio(websocket: WebSocket, audio_url: str, song_request_id: str, index: int, model_name: str):
    try:
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
    except Exception as e:
        logger.error(f"트랙 {index} 처리 중 에러 발생: {str(e)}")
        raise

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    song_request_id = generate_random_identifier()
    
    try:
        await websocket.accept()
        active_connections[song_request_id] = websocket
        
        # 데이터 수신
        try:
            data = await websocket.receive_json()
        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "error": "invalid_data",
                "message": "잘못된 데이터 형식입니다"
            })
            return

        # Suno 오디오 생성
        try:
            result = await generate_audio(
                data["lyric"],
                data["title"],
                data["style"],
                data["style_negative"]
            )
        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "error": "suno_generation_failed",
                "message": "Suno 오디오 생성에 실패했습니다"
            })
            return

        # 오디오 트랙 처리
        try:
            await websocket.send_json({"status": "processing_started"})
            
            tasks = [
                asyncio.create_task(process_single_audio(
                    websocket, 
                    result["data"][i]["audio_url"],
                    song_request_id, 
                    i+1, 
                    data["modelName"]
                )) for i in range(2)
            ]

            for completed_task in asyncio.as_completed(tasks):
                try:
                    result_path = await completed_task
                    await websocket.send_json({
                        "status": "track_completed",
                        "resultUrl": result_path
                    })
                except Exception as e:
                    await websocket.send_json({
                        "status": "error",
                        "error": "track_processing_failed",
                        "message": f"트랙 처리 중 실패: {str(e)}"
                    })
                    return

            await websocket.send_json({"status": "all_completed"})

        except Exception as e:
            await websocket.send_json({
                "status": "error",
                "error": "processing_failed",
                "message": f"오디오 처리 중 실패: {str(e)}"
            })
            
    except Exception as e:
        logger.error(f"웹소켓 처리 중 에러: {str(e)}")
        try:
            await websocket.send_json({
                "status": "error",
                "error": "system_error",
                "message": "시스템 에러가 발생했습니다"
            })
        except:
            pass
    
    finally:
        if song_request_id in active_connections:
            del active_connections[song_request_id]

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)