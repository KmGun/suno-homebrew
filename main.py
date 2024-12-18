from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from uvr import download_mp3, separate_audio_tracks
from aicover.aicover import AICoverProcessor


# FastAPI 인스턴스 생성
app = FastAPI()

# # 데이터 모델 정의
class requestBody(BaseModel):
    modelName : str
    guideAudioUrl : str


# POST 요청 처리 - 새 아이템 생성
@app.post("/", response_model=requestBody)
async def receive_request(item: requestBody):
    request_body = item.model_dump()
    # print(request_body)

    # # 1. 음원 다운로드 - await로 완료될 때까지 대기하고 로컬 파일 경로 받기
    # print("음원 다운로드 시작")
    # local_file_path = await download_mp3(request_body["guideAudioUrl"])
    
    # # 2. 음원 분리 - 다운로드된 로컬 파일 경로를 전달
    # print("음원 분리 시작")
    # result = await separate_audio_tracks(local_file_path)

    # 3. 추론
    gvocal_path = "temp/u1FYiuqP/u1FYiuqP_gvocal.mp3"
    mr_path = "temp/u1FYiuqP/u1FYiuqP_mr.mp3"
    aicover_processor = AICoverProcessor(os.getenv("AWS_ACCESS_KEY"), os.getenv("AWS_SECRET_KEY"))
    aicover_processor.process_cover(gvocal_path, mr_path, "ljb", "u1FYiuqP")

    return item



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)