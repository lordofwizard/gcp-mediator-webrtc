import asyncio
import websockets

connected = set()

async def handler(websocket, path):
    # Register.
    connected.add(websocket)
    try:
        async for message in websocket:
	    for conn in connected:
                if conn != websocket:
                    await conn.send(message)
    finally:
        connected.remove(websocket)

start_server = websockets.serve(handler, "localhost", 8080)

print("Signaling server running on ws://localhost:8080")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

