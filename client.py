# receiver.py
import cv2
import asyncio
import socketio
from aiortc import RTCPeerConnection, RTCIceCandidate, RTCSessionDescription, VideoStreamTrack
from utils import candidate_to_json, description_to_json, json_to_candidate, json_to_description

sio = socketio.Client()

class VideoReceiver(VideoStreamTrack):
    def __init__(self):
        super().__init__()

    async def recv(self):
        frame = await super().recv()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('Received Video', frame)
        cv2.waitKey(1)
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

    @pc.on("track")
    def on_track(track):
        pc.addTrack(VideoReceiver())

    @sio.event
    async def message(data):
        if 'sdp' in data:
            await pc.setRemoteDescription(json_to_description(data))
        elif 'candidate' in data:
            await pc.addIceCandidate(json_to_candidate(data))

    # send answer
    await pc.setLocalDescription(await pc.createAnswer())
    sio.emit('message', description_to_json(pc.localDescription))

async def main():
    pc = RTCPeerConnection()
    sio.connect('http://localhost:8765')
    await run(pc)

if __name__ == "__main__":
    asyncio.run(main())

