# sender.py
import cv2
import asyncio
import websockets
from aiortc import RTCIceCandidate, RTCPeerConnection, RTCSessionDescription, VideoStreamTrack

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

async def run(pc, signaling):
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        await signaling.send(candidate_to_json(candidate))

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        if pc.iceConnectionState == "failed":
            await pc.close()
            await signaling.close()

    # send offer
    await pc.setLocalDescription(await pc.createOffer())
    await signaling.send(description_to_json(pc.localDescription))

    # receive answer
    answer = await signaling.recv()
    await pc.setRemoteDescription(json_to_description(answer))

    # consume signaling
    while True:
        obj = await signaling.recv()
        if isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)

async def main():
    pc = RTCPeerConnection()
    pc.addTrack(VideoTrack())

    signaling = await websockets.connect("ws://localhost:6969")
    await run(pc, signaling)

if __name__ == "__main__":
    asyncio.run(main())

