# sender.py
import cv2
import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from utils import candidate_to_json, description_to_json, json_to_candidate, json_to_description

sio = socketio.Client()

class VideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

async def run(pc):
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        sio.emit('message', candidate_to_json(candidate))

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()
            sio.disconnect()

    @sio.event
    async def message(data):
        if 'sdp' in data:
            await pc.setRemoteDescription(json_to_description(data))
        elif 'candidate' in data:
            await pc.addIceCandidate(json_to_candidate(data))

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    sio.emit('message', description_to_json(pc.localDescription))

async def main():
    pc = RTCPeerConnection()
    pc.addTrack(VideoTrack())

    sio.connect('http://localhost:8765')
    await run(pc)

if __name__ == "__main__":
    asyncio.run(main())

