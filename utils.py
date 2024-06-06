# utils.py
import json
from aiortc import RTCIceCandidate, RTCSessionDescription

def candidate_to_json(candidate):
    return json.dumps({
        "candidate": candidate.candidate,
        "sdpMid": candidate.sdpMid,
        "sdpMLineIndex": candidate.sdpMLineIndex,
    })

def description_to_json(description):
    return json.dumps({
        "sdp": description.sdp,
        "type": description.type,
    })

def json_to_candidate(data):
    return RTCIceCandidate(
        sdpMid=data["sdpMid"],
        sdpMLineIndex=data["sdpMLineIndex"],
        candidate=data["candidate"],
    )

def json_to_description(data):
    return RTCSessionDescription(
        sdp=data["sdp"],
        type=data["type"],
    )

