from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import asyncio
from typing import Dict, List
from datetime import datetime

app = FastAPI()

# CORS 설정 (VSCode extension과 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 연결된 클라이언트 관리
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {"message": "AI Live Coding Interview Server is running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message = json.loads(data)
            
            print(f"Received: {message}")
            
            # 메시지 타입에 따른 처리
            if message.get("type") == "code_update":
                # 코드 분석 로직
                response = {
                    "type": "analysis",
                    "data": {
                        "status": "analyzing",
                        "timestamp": datetime.now().isoformat()
                    }
                }
                await manager.send_message(json.dumps(response), websocket)
                
            elif message.get("type") == "start_interview":
                # 인터뷰 시작 로직
                response = {
                    "type": "interview_started",
                    "data": {
                        "message": "Interview session started",
                        "sessionId": "session_123"
                    }
                }
                await manager.send_message(json.dumps(response), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)