import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaPlayer

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track):
        super().__init__()
        self.track = track

    async def recv(self):
        frame = await self.track.recv()
        return frame

async def run_offer(pc):
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    print("Offer SDP:")
    print(offer.sdp)
    return offer

async def main():
    pc = RTCPeerConnection(configuration={"iceServers": [{"urls": "stun:stun.4.google.com:19302"}]})
    player = MediaPlayer('/dev/video0')  # Use the correct device for your webcam
    pc.addTrack(VideoTransformTrack(player.video))

    offer = await run_offer(pc)
    with open('offer.sdp', 'w') as f:
        f.write(offer.sdp)

    print("Offer written to offer.sdp")
    input("Press Enter after receiver sets remote description...")

    with open('answer.sdp', 'r') as f:
        answer_sdp = f.read()

    answer = RTCSessionDescription(sdp=answer_sdp, type='answer')
    await pc.setRemoteDescription(answer)
    print("Remote description set")

if __name__ == "__main__":
    asyncio.run(main())

