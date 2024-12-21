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

async def process_single_audio(websocket: WebSocket, audio_url: str, song_request_id: str, index: int, model_name: str):
    print(f"🎵 트랙 {index} 처리 시작...")
    print(f"📥 MP3 다운로드 시작: {audio_url}")
    local_file_path = await download_mp3(audio_url, song_request_id, index)
    print(f"✅ MP3 다운로드 완료: {local_file_path}")
    
    print(f"🎼 트랙 분리 시작: {local_file_path}")
    separated_result = await separate_audio_tracks(local_file_path, song_request_id, index)
    print(f"✅ 트랙 분리 완료")
    
    print(f"🎤 AI 커버 처리 시작")
    aicover_processor = AICoverProcessor()
    result_path = await aicover_processor.process_cover(
        guide_path=separated_result['vocal'],
        model_name=model_name,
        song_request_id=song_request_id,
        index=index
    )
    print(f"✅ AI 커버 처리 완료: {result_path}")
    
    return result_path

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        print("✅ 웹소켓 연결 수락됨")
        song_request_id = None
        
        data = await websocket.receive_json()
        print(f"📥 받은 데이터: {data}")
        
        song_request_id = generate_random_identifier()
        active_connections[song_request_id] = websocket
        print(f"🆔 생성된 요청 ID: {song_request_id}")
        
        await websocket.send_json({
            "status": "accepted",
            "songRequestId": song_request_id,
            "message": "신청곡이 접수되었습니다."
        })
        print("✅ 접수 완료 메시지 전송")
        
        print("🎵 Suno 오디오 생성 시작...")
        await websocket.send_json({"status": "generating original audio"})
        result = await generate_audio(data["lyric"], data["title"], data["style"], data["style_negative"])
        print("✅ Suno 오디오 생성 완료")
        
        await websocket.send_json({"status": "processing audio tracks"})
        print("🎼 오디오 트랙 처리 시작...")

        task1 = asyncio.create_task(
            process_single_audio(
                websocket, 
                result.data[0]["audio_url"], 
                song_request_id, 
                1, 
                data["modelName"]
            )
        )
        task2 = asyncio.create_task(
            process_single_audio(
                websocket, 
                result.data[1]["audio_url"], 
                song_request_id, 
                2, 
                data["modelName"]
            )
        )
        print("✅ 오디오 처리 태스크 생성 완료")

        for completed_task in asyncio.as_completed([task1, task2]):
            result_path = await completed_task
            await websocket.send_json({
                "status": "track_completed",
                "resultUrl": result_path
            })
            print(f"✅ 트랙 처리 완료: {result_path}")
        
        await websocket.send_json({
            "status": "all_completed"
        })
        print("🎉 모든 처리 완료!")
            
    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        if song_request_id and song_request_id in active_connections:
            del active_connections[song_request_id]
            print(f"🔌 연결 종료: {song_request_id}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)