import cv2
import numpy as np
import os
import time
from hardware import get_hardware

class TrailSenseCore:
    def __init__(self, camera_source=0):
        # Feature Extraction Configuration
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # State
        self.landmarks = [] 
        self.mode = "EXPLORE"
        self.last_capture_time = 0
        self.capture_interval = 2.5 
        self.current_match_score = 0.0
        self.best_match_id = -1
        self.status_message = "SYSTEM INITIALIZING"
        self.landmark_dir = "landmarks_data"
        self.hw = get_hardware()
        
        # Camera Configuration
        self.camera_source = 0
        if isinstance(camera_source, str) and camera_source.startswith("http"):
            self.camera_source = camera_source
        elif str(camera_source).isdigit():
            self.camera_source = int(camera_source)
            
        print(f"TrailSense Core Initialized. Source: {self.camera_source}")
        
        if not os.path.exists(self.landmark_dir):
            os.makedirs(self.landmark_dir)

    def set_mode(self, mode):
        self.mode = mode
        if mode == "EXPLORE":
            self.status_message = "EXPLORATION MODE ACTIVE"
            self.hw.set_led("GREEN")
        elif mode == "RETURN":
            self.status_message = "RETURN NAVIGATION ACTIVE"
            self.hw.set_led("AMBER")
            
    def process_frame(self, frame):
        # Preprocessing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Feature Extraction
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        vis_frame = frame.copy()
        
        if self.mode == "EXPLORE":
            current_time = time.time()
            if current_time - self.last_capture_time > self.capture_interval:
                # Qualification check for landmark quality
                if descriptors is not None and len(keypoints) > 50:
                    self._save_landmark(frame, keypoints, descriptors)
                    self.last_capture_time = current_time
                    self.status_message = "LANDMARK CAPTURED"
                    self.hw.set_led("GREEN") 
            
            # Visualize Active Features
            cv2.drawKeypoints(vis_frame, keypoints, vis_frame, color=(0, 255, 0), flags=0)

        elif self.mode == "RETURN":
            if descriptors is not None and len(self.landmarks) > 0:
                best_score = 0
                best_id = -1
                
                # Global Search (Optimization: constrained window search in future based on last known loc)
                for lm in self.landmarks:
                    if lm['descriptors'] is None: continue
                    matches = self.bf.match(descriptors, lm['descriptors'])
                    
                    # Filtering valid matches
                    good_matches = [m for m in matches if m.distance < 50]
                    score = len(good_matches)
                    
                    if score > best_score:
                        best_score = score
                        best_id = lm['id']

                # Normalize score (0-100) based on empirical feature density
                normalized_score = min(100, (best_score / 50.0) * 100)
                self.current_match_score = normalized_score
                self.best_match_id = best_id
                
                # Feedback Loop
                if normalized_score > 70:
                    self.status_message = f"MATCH FOUND (ID: {best_id})"
                    color = (0, 255, 0)
                    self.hw.set_led("GREEN")
                elif normalized_score > 30:
                    self.status_message = "POSSIBLE MATCH..."
                    color = (0, 255, 255)
                    self.hw.set_led("AMBER")
                else:
                    self.status_message = "OFF TRACK"
                    color = (0, 0, 255)
                    self.hw.set_led("RED")
                
                # User Guidance Overlay
                if best_id != -1:
                    lm = next((l for l in self.landmarks if l['id'] == best_id), None)
                    if lm:
                        matches = self.bf.match(descriptors, lm['descriptors'])
                        good_matches = [m for m in matches if m.distance < 50]
                        matched_pts = [keypoints[m.queryIdx].pt for m in good_matches]
                        
                        # Highlight matching features
                        for pt in matched_pts:
                            cv2.circle(vis_frame, (int(pt[0]), int(pt[1])), 4, color, 1)
                            
                cv2.putText(vis_frame, f"CONFIDENCE: {int(normalized_score)}%", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            else:
                self.status_message = "NO LANDMARKS STORED"
                self.hw.set_led("RED")

        return vis_frame

    def _save_landmark(self, frame, keypoints, descriptors):
        lm_id = len(self.landmarks)
        filename = f"{self.landmark_dir}/landmark_{lm_id}.jpg"
        cv2.imwrite(filename, frame)
        
        self.landmarks.append({
            'id': lm_id,
            'descriptors': descriptors,
            'timestamp': time.time()
        })
        # print(f"Captured Landmark {lm_id}") # Debug only

    def get_state(self):
        return {
            "mode": self.mode,
            "status": self.status_message,
            "confidence": self.current_match_score,
            "landmark_count": len(self.landmarks),
            "best_match": self.best_match_id,
            "camera_source": self.camera_source if isinstance(self.camera_source, str) else "Webcam"
        }
