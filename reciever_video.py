import cv2
import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("Receiver", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()
        return frame

async def run_answer(pc, offer):
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    print("Answer SDP:")
    print(answer.sdp)
    return answer

async def main():
    pc = RTCPeerConnection()
    pc.addIceServer({"urls": "stun:stun.l.google.com:19302"})

    @pc.on("track")
    def on_track(track):
        if track.kind == "video":
            pc.addTrack(VideoTransformTrack(track))

    with open('offer.sdp', 'r') as f:
        offer_sdp = f.read()

    offer = RTCSessionDescription(sdp=offer_sdp, type='offer')
    answer = await run_answer(pc, offer)
    answer_sdp = answer.sdp

    with open('answer.sdp', 'w') as f:
        f.write(answer_sdp)

    print("Answer written to answer.sdp")
    input("Press Enter to exit...")

if __name__ == "__main__":
    asyncio.run(main())

