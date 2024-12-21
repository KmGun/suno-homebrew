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
        print("\n=== 웹소켓 연결 시작 ===")
        await websocket.accept()
        print("1. ✅ 웹소켓 연결 수락됨")
        song_request_id = None
        
        try:
            data = await websocket.receive_json()
            print("2. 📥 받은 데이터:", data)
            print("3. 📋 데이터 타입 확인:")
            for key, value in data.items():
                print(f"   - {key}: {type(value)} = {value}")
        except Exception as e:
            print("❌ 데이터 수신 중 에러:", str(e))
            raise e
        
        try:
            print("\n=== Suno 처리 시작 ===")
            print("4. 🎵 generate_audio 함수 호출 직전")
            print(f"   - lyric: {data['lyric']}")
            print(f"   - title: {data['title']}")
            print(f"   - style: {data['style']}")
            print(f"   - style_negative: {data['style_negative']}")
            
            result = await generate_audio(
                data["lyric"],
                data["title"],
                data["style"],
                data["style_negative"]
            )
            print("5. ✅ generate_audio 함수 완료")
            print("6. 📦 반환된 결과:", result)
            
        except Exception as e:
            print(f"❌ Suno 처리 중 에러 발생:")
            print(f"   - 에러 타입: {type(e)}")
            print(f"   - 에러 메시지: {str(e)}")
            print(f"   - 에러 위치: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
            raise e

        try:
            print("\n=== 오디오 처리 시작 ===")
            print("7. 🎼 오디오 트랙 처리 태스크 생성")
            task1 = asyncio.create_task(
                process_single_audio(
                    websocket, 
                    result["data"][0]["audio_url"],
                    song_request_id, 
                    1, 
                    data["modelName"]
                )
            )
            task2 = asyncio.create_task(
                process_single_audio(
                    websocket, 
                    result["data"][1]["audio_url"],
                    song_request_id, 
                    2, 
                    data["modelName"]
                )
            )
            print("8. ✅ 태스크 생성 완료")
            
        except Exception as e:
            print(f"❌ 태스크 생성 중 에러:")
            print(f"   - 에러 타입: {type(e)}")
            print(f"   - 에러 메시지: {str(e)}")
            raise e

        try:
            await websocket.send_json({"status": "processing audio tracks"})
            print("🎼 오디오 트랙 처리 시작...")

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
            print(f"❌ Suno 오디오 생성 중 에러 발생: {str(e)}")
            print(f"❌ 에러 타입: {type(e)}")
            raise e
            
    except Exception as e:
        print(f"\n=== ❌ 최종 에러 ===")
        print(f"에러 타입: {type(e)}")
        print(f"에러 메시지: {str(e)}")
        await websocket.send_json({"status": "error", "message": str(e)})
    finally:
        if song_request_id and song_request_id in active_connections:
            del active_connections[song_request_id]
            print(f"\n=== 🔌 연결 종료: {song_request_id} ===")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)