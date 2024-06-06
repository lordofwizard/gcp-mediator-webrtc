# signaling_server.py
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)

connections = {}

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)
    connections[sid] = sio

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)
    connections.pop(sid, None)

@sio.event
def message(sid, data):
    print('Message from', sid, ':', data)
    for conn_sid in connections:
        if conn_sid != sid:
            sio.emit('message', data, room=conn_sid)

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    import os

    port = int(os.getenv('PORT', 8765))
    eventlet.wsgi.server(eventlet.listen(('localhost', port)), app)

