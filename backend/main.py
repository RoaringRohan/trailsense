from fastapi import FastAPI, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import typing
import os
import requests
import numpy as np
from vision_core import TrailSenseCore
import uvicorn
import time
import argparse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
parser = argparse.ArgumentParser()
parser.add_argument("--source", default=os.getenv("CAMERA_SOURCE", "0"), help="Camera source URL or ID")
args, _ = parser.parse_known_args()

core = TrailSenseCore(camera_source=args.source)
camera = None

def get_camera():
    global camera
    if camera is None:
        src = core.camera_source
        if str(src).isdigit():
            src = int(src)
        camera = cv2.VideoCapture(src)
    return camera

def generate_frames():
    """
    Video streaming generator. 
    Handles connection recovery for IP cameras (ESP32) automatically.
    """
    global camera
    cam = get_camera()
    while True:
        if not cam.isOpened():
            # Attempt reconnection
            src = core.camera_source
            if str(src).isdigit(): src = int(src)
            cam.open(src)
            time.sleep(1)
            continue
            
        success, frame = cam.read()
        if not success:
            time.sleep(0.1)
            continue
            
        processed_frame = core.process_frame(frame)
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/video_feed")
def video_feed():
    return Response(generate_frames(), media_type='multipart/x-mixed-replace; boundary=frame')

@app.get("/status")
def get_status():
    return core.get_state()

@app.post("/set_mode/{mode}")
def set_mode(mode: str):
    if mode in ["EXPLORE", "RETURN"]:
        core.set_mode(mode)
        return {"success": True, "mode": mode}
    return {"success": False, "error": "Invalid mode"}

@app.post("/update_source")
def update_source(source_url: str):
    """Runtime camera source update"""
    global camera, core
    core.camera_source = source_url
    if camera:
        camera.release()
    camera = None 
    return {"success": True, "source": source_url}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
