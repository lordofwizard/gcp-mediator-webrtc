const wrtc = require('wrtc');
const WebSocket = require('ws');
const NodeWebcam = require('node-webcam');
const fs = require('fs');

const signalingServerUrl = 'ws://192.168.0.239:6969';
const captureInterval = 100; // Capture interval in milliseconds

let pc = new wrtc.RTCPeerConnection();
let signalingSocket = new WebSocket(signalingServerUrl);

// Set up webcam capture
const Webcam = NodeWebcam.create({
    width: 640,
    height: 480,
    quality: 100,
    frames: 30,
    saveShots: false,
    output: "jpeg",
    device: false,
    callbackReturn: "buffer",
    verbose: false
});

async function captureAndSendFrame() {
    Webcam.capture("frame", (err, data) => {
        if (err) {
            console.error("Error capturing frame:", err);
            return;
        }

        let videoTrack = new wrtc.MediaStreamTrack({
            kind: 'video',
            label: 'webcam',
            id: 'webcam0',
            enabled: true,
            readyState: 'live'
        });

        videoTrack.onended = () => {
            console.log('Video track ended');
        };

        videoTrack.contentHint = 'motion';
        videoTrack.mediaSource = 'webcam';

        const stream = new wrtc.MediaStream([videoTrack]);
        stream.addTrack(videoTrack);

        pc.addTrack(videoTrack, stream);

        setTimeout(captureAndSendFrame, captureInterval);
    });
}

async function start() {
    // Connect to the signaling server
    signalingSocket.onmessage = async (message) => {
        const signal = JSON.parse(message.data);
        if (signal.answer) {
            await pc.setRemoteDescription(new wrtc.RTCSessionDescription(signal.answer));
        } else if (signal.iceCandidate) {
            await pc.addIceCandidate(new wrtc.RTCIceCandidate(signal.iceCandidate));
        }
    };

    // Handle ICE candidates
    pc.onicecandidate = (event) => {
        if (event.candidate) {
            signalingSocket.send(JSON.stringify({ iceCandidate: event.candidate }));
        }
    };

    // Create and send offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    signalingSocket.onopen = () => {
        signalingSocket.send(JSON.stringify({ offer: offer }));
    };

    captureAndSendFrame();
}

start();
