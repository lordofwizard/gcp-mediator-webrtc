import asyncio
import cv2
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from av import VideoFrame

class VideoTrack(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        ret, frame = self.cap.read()
        if not ret:
            return

        # Convert to video frame
        video_frame = VideoFrame.from_ndarray(frame, format="bgr24")
        video_frame.pts = pts
        video_frame.time_base = time_base
        return video_frame

async def run(pc, signaling):
    @pc.on("icecandidate")
    async def on_icecandidate(candidate):
        if candidate:
            await signaling.send(json.dumps({"iceCandidate": candidate}))

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"ICE connection state is {pc.iceConnectionState}")
        if pc.iceConnectionState == "failed":
            await pc.close()

    # Add video track
    video_track = VideoTrack()
    pc.addTrack(video_track)

    # Send offer
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await signaling.send(json.dumps({"offer": offer}))

    while True:
        message = json.loads(await signaling.recv())
        if "answer" in message:
            await pc.setRemoteDescription(RTCSessionDescription(sdp=message["answer"]["sdp"], type=message["answer"]["type"]))
        elif "iceCandidate" in message:
            candidate = message["iceCandidate"]
            await pc.addIceCandidate(candidate)

async def main():
    signaling = await websockets.connect("ws://192.168.0.239:6969")
    pc = RTCPeerConnection()
    await run(pc, signaling)

if __name__ == "__main__":
    asyncio.run(main())
