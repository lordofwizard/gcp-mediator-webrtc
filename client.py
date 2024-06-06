# receiver.py
import cv2
import asyncio
import websockets
from aiortc import RTCPeerConnection, RTCIceCandidate, RTCSessionDescription, VideoStreamTrack

class VideoReceiver(VideoStreamTrack):
    def __init__(self):
        super().__init__()

    async def recv(self):
        frame = await super().recv()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        cv2.imshow('Received Video', frame)
        cv2.waitKey(1)
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

    @pc.on("track")
    def on_track(track):
        pc.addTrack(VideoReceiver())

    # receive offer
    offer = await signaling.recv()
    await pc.setRemoteDescription(json_to_description(offer))

    # send answer
    await pc.setLocalDescription(await pc.createAnswer())
    await signaling.send(description_to_json(pc.localDescription))

    # consume signaling
    while True:
        obj = await signaling.recv()
        if isinstance(obj, RTCIceCandidate):
            await pc.addIceCandidate(obj)

async def main():
    pc = RTCPeerConnection()
    signaling = await websockets.connect("ws://localhost:6969")
    await run(pc, signaling)

if __name__ == "__main__":
    asyncio.run(main())

