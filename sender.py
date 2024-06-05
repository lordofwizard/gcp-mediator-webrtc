import cv2
import asyncio
import websockets
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer

# STUN server configuration
stun_server = "59.11.25.32:6969"

class VideoStreamTrackFromCamera(VideoStreamTrack):
    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)

    async def recv(self):
        frame = await self.next_timestamp()
        ret, img = self.cap.read()
        if not ret:
            raise Exception("Failed to capture image from camera")
        return frame, img

async def sender(websocket, path):
    pc = RTCPeerConnection({"iceServers": [{"urls": f"stun:{stun_server}"}]})
    video_track = VideoStreamTrackFromCamera()
    pc.addTrack(video_track)
    
    offer = await websocket.recv()
    offer = RTCSessionDescription(sdp=offer, type='offer')
    await pc.setRemoteDescription(offer)
    
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    await websocket.send(pc.localDescription.sdp)

start_server = websockets.serve(sender, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

