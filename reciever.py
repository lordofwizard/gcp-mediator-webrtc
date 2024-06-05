import cv2
import asyncio
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription

# STUN server configuration
stun_server = "59.11.25.32:6969"

async def receiver(websocket, path):
    pc = RTCPeerConnection({"iceServers": [{"urls": f"stun:{stun_server}"}]})

    async def on_track(track):
        if track.kind == "video":
            while True:
                frame = await track.recv()
                img = frame.to_ndarray(format="bgr24")
                cv2.imshow("Received", img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    pc.on("track", on_track)
    
    offer = await pc.createOffer()
    await pc.setLocalDescription(offer)
    await websocket.send(pc.localDescription.sdp)
    
    answer = await websocket.recv()
    answer = RTCSessionDescription(sdp=answer, type='answer')
    await pc.setRemoteDescription(answer)

start_server = websockets.serve(receiver, "0.0.0.0", 8766)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

