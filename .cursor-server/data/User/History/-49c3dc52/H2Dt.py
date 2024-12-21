from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import uvicorn
import asyncio
from typing import Dict
from src.execute import AICoverProcessor
from suno import generate_audio
from tools import generate_random_identifier, download_mp3
import logging
from uvr import SubprocessBasedSeparator

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
active_connections: Dict[str, WebSocket] = {}

# 클래스 인스턴스 생성
separator = SubprocessBasedSeparator(base_dir='/app')

async def process_single_audio(websocket: WebSocket, audio_url: str, song_request_id: str, index: int, model_name: str):
    try:
        local_file_path = await download_mp3(audio_url, song_request_id, index)
        result_paths = await separator.separate_audio_tracks(
            input_file_path=local_file_path,
            song_request_id=song_request_id,
            file_number=index
        )
        
        # 디버깅용 임시 데이터

        result_paths = {
            'mr': '/app/temp/PkP87Uqm/temp_2_(Instrumental)_Kim_Vocal_1.mp3',
            'chorus': '/app/temp/PkP87Uqm/temp_2_(Vocals)_Kim_Vocal_1_(Instrumental)_6_HP-Karaoke-UVR.mp3', 
            'vocal': '/app/temp/PkP87Uqm/temp_2_(Vocals)_Kim_Vocal_1_(Vocals)_6_HP-Karaoke-UVR_(Instrumental)_Reverb_HQ_By_FoxJoy_(Instrumental)_UVR-DeNoise.mp3'
        }

        aicover_processor = AICoverProcessor()
        result_urls = aicover_processor.process_cover(
            guide_path=result_paths['vocal'],
            model_name=model_name,
            song_request_id=song_request_id,
            index=index
        )
        
        if not result_urls:
            raise Exception("AI 커버 생성 실패")
            
        # 각 결과 URL에 대해 개별적으로 완료 메시지 전송
        for url in result_urls:
            await websocket.send_json({
                "status": "track_completed",
                "resultUrl": url
            })
            
        return True  # 성공적으로 처리됨을 나타냄
        
    except Exception as e:
        logger.error(f"트랙 {index} 처리 중 에러 발생: {str(e)}")
        raise

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    print("🔵 웹소켓 연결 시도")
    song_request_id = generate_random_identifier()
    
    try:
        await websocket.accept()
        print("✅ 웹소켓 연결 성공")
        
        # 즉시 연결 성공 메시지 전송
        await websocket.send_json({
            "status": "connected",
            "message": "웹소켓 연결됨"
        })
        print("📤 연결 성공 메시지 전송됨")
        
        # 데이터 수신
        data = await websocket.receive_json()
        print(f"📥 받은 데이터: {data}")
        
        # 데이터 수신 확인 메시지 즉시 전송
        await websocket.send_json({
            "status": "received",
            "message": "데이터 수신 완료"
        })
        print("📤 데이터 수신 확인 메시지 전송됨")
        
        # Suno 오디오 생성
        try:
            print("🎵 Suno 오디오 생성 시작")
            result = await generate_audio(
                data["lyric"],
                data["title"],
                data["style"],
                data["style_negative"]
            )
            print("✅ Suno 오디오 생성 완료")
        except Exception as e:
            print(f"❌ Suno 오디오 생성 실패: {str(e)}")
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
        print(f"❌ 웹소켓 처리 중 에러: {str(e)}")
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