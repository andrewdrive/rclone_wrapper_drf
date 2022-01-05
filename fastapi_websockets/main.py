import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket
from request_to_rclone import RcloneClient
from exceptions import *


app = FastAPI(title='WebSocket for rclone job/status')

rclone_client = RcloneClient(host_name='rclone', port=8002)

@app.websocket('/ws/{job_id}')
async def websocket_endpoint(websocket: WebSocket, job_id: int):
       await websocket.accept()
       while True:
              await asyncio.sleep(3)
              try:
                     data = rclone_client.core_stats(jobid=job_id)
              except RcloneJobStatusError as je:
                     data = je.message
              await websocket.send_json(data)


if __name__ == '__main__':
       uvicorn.run('main:app', host="0.0.0.0", port=8003, reload=True)