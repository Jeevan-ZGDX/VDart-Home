"""Vision Module for CMFH
Real-time pose detection and body language analysis using pure MediaPipe
NO OpenCV dependencies - uses MediaPipe + PIL/numpy exclusively
"""

import base64
import numpy as np
from PIL import Image
import io
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class PoseMetrics:
    """Pose analysis metrics"""
    posture_score: float
    hand_gesture: str
    arm_position: str
    shoulder_balance: float
    confidence_level: str
    suggestions: List[str]


class PoseAnalyzer:
    """Analyze body language and pose from camera"""

    def __init__(self):
        self._mp_pose = None
        self._mp_drawing = None
        self._pose = None

    def _load_media_pipe(self):
        """Lazy load MediaPipe"""
        if self._pose is None:
            import mediapipe as mp
            self._mp_pose = mp.solutions.pose
            self._mp_drawing = mp.solutions.drawing_utils
            self._pose = self._mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                smooth_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )

    def decode_base64_frame(self, base64_string: str) -> Optional[np.ndarray]:
        """Decode base64 image frame to numpy array without OpenCV"""
        try:
            # Decode base64 to bytes
            img_bytes = base64.b64decode(base64_string)
            # Open with PIL
            img = Image.open(io.BytesIO(img_bytes))
            # Convert to numpy array (already RGB format from PIL)
            return np.array(img)
        except Exception as e:
            print(f"Frame decode error: {e}")
            return None

    def analyze_frame(self, frame_data) -> Dict[str, Any]:
        """Analyze a single frame for pose - accepts numpy array OR base64 string"""
        self._load_media_pipe()

        # Handle base64 input from frontend
        if isinstance(frame_data, str):
            frame = self.decode_base64_frame(frame_data)
            if frame is None:
                return {"detected": False, "message": "Could not decode frame"}
        else:
            frame = frame_data

        # Frame is already RGB from PIL, process directly with MediaPipe
        results = self._pose.process(frame)

        if not results.pose_landmarks:
            return {
                "detected": False,
                "message": "No person detected in frame"
            }

        landmarks = results.pose_landmarks.landmark

        posture_score = self._calculate_posture_score(landmarks)
        hand_gesture = self._detect_hand_gesture(landmarks)
        arm_position = self._detect_arm_position(landmarks)
        shoulder_balance = self._calculate_shoulder_balance(landmarks)
        confidence = self._assess_confidence(landmarks)

        return {
            "detected": True,
            "posture_score": posture_score,
            "hand_gesture": hand_gesture,
            "arm_position": arm_position,
            "shoulder_balance": shoulder_balance,
            "confidence_level": confidence,
            "suggestions": self._generate_suggestions(
                posture_score, hand_gesture, arm_position, shoulder_balance
            ),
            "landmarks": self._get_key_points(landmarks)
        }

    def _calculate_posture_score(self, landmarks) -> float:
        """Calculate posture score"""
        try:
            nose = landmarks[0]
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]
            left_hip = landmarks[23]
            right_hip = landmarks[24]

            shoulder_mid_x = (left_shoulder.x + right_shoulder.x) / 2
            hip_mid_x = (left_hip.x + right_hip.x) / 2
            nose_x = nose.x

            alignment = abs(nose_x - ((shoulder_mid_x + hip_mid_x) / 2))

            vertical_score = max(0, 100 - alignment * 500)

            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            if 0.1 < shoulder_width < 0.4:
                width_score = 100
            else:
                width_score = max(0, 100 - abs(shoulder_width - 0.25) * 200)

            posture_score = (vertical_score * 0.6 + width_score * 0.4)
            return round(posture_score, 1)
        except:
            return 50.0

    def _detect_hand_gesture(self, landmarks) -> str:
        """Detect hand gesture"""
        try:
            left_wrist = landmarks[15]
            right_wrist = landmarks[16]
            left_elbow = landmarks[13]
            right_elbow = landmarks[14]

            left_hand_up = left_wrist.y < left_elbow.y
            right_hand_up = right_wrist.y < right_elbow.y

            if left_hand_up and right_hand_up:
                return "both_arms_raised"
            elif left_hand_up:
                return "left_hand_up"
            elif right_hand_up:
                return "right_hand_up"
            else:
                return "hands_down"
        except:
            return "unknown"

    def _detect_arm_position(self, landmarks) -> str:
        """Detect arm position"""
        try:
            left_shoulder = landmarks[11]
            left_elbow = landmarks[13]
            left_wrist = landmarks[15]

            right_shoulder = landmarks[12]
            right_elbow = landmarks[14]
            right_wrist = landmarks[16]

            left_angle = self._calculate_angle(
                (left_shoulder.x, left_shoulder.y),
                (left_elbow.x, left_elbow.y),
                (left_wrist.x, left_wrist.y)
            )

            right_angle = self._calculate_angle(
                (right_shoulder.x, right_shoulder.y),
                (right_elbow.x, right_elbow.y),
                (right_wrist.x, right_wrist.y)
            )

            if left_angle > 150 and right_angle > 150:
                return "arms_open"
            elif left_angle < 90 and right_angle < 90:
                return "arms_crossed"
            elif left_angle < 60 or right_angle < 60:
                return "hand_on_hip"
            else:
                return "relaxed"
        except:
            return "unknown"

    def _calculate_angle(self, p1: Tuple, p2: Tuple, p3: Tuple) -> float:
        """Calculate angle between three points"""
        try:
            v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
            v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])

            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))
            return angle
        except:
            return 90.0

    def _calculate_shoulder_balance(self, landmarks) -> float:
        """Calculate shoulder balance"""
        try:
            left_shoulder = landmarks[11]
            right_shoulder = landmarks[12]

            balance = 100 - abs(left_shoulder.y - right_shoulder.y) * 200
            return max(0, round(balance, 1))
        except:
            return 50.0

    def _assess_confidence(self, landmarks) -> str:
        """Assess confidence from pose"""
        try:
            chin = landmarks[0]
            shoulder_mid_y = (landmarks[11].y + landmarks[12].y) / 2

            chin_height = 1 - chin.y
            shoulder_width = abs(landmarks[11].x - landmarks[12].x)

            if chin_height > 0.3 and shoulder_width > 0.15:
                return "high"
            elif chin_height > 0.15:
                return "medium"
            else:
                return "low"
        except:
            return "unknown"

    def _generate_suggestions(
        self,
        posture: float,
        hand: str,
        arm: str,
        shoulders: float
    ) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []

        if posture < 70:
            suggestions.append("Stand straighter - align your head, shoulders, and hips")

        if hand == "hands_down":
            suggestions.append("Use hand gestures to emphasize key points")
        elif hand == "both_arms_raised":
            suggestions.append("Great energy! Keep it balanced")

        if arm == "arms_crossed":
            suggestions.append("Open your arms to appear more approachable")

        if shoulders < 70:
            suggestions.append("Keep shoulders level and relaxed")

        if not suggestions:
            suggestions.append("Great posture! Maintain this during speaking")

        return suggestions

    def _get_key_points(self, landmarks) -> Dict[str, Tuple[float, float]]:
        """Extract key landmarks"""
        key_points = {}
        try:
            indices = [0, 11, 12, 13, 14, 15, 16, 23, 24]
            names = ["nose", "left_shoulder", "right_shoulder", "left_elbow",
                     "right_elbow", "left_wrist", "right_wrist", "left_hip", "right_hip"]

            for i, name in zip(indices, names):
                lm = landmarks[i]
                key_points[name] = (lm.x, lm.y)
        except:
            pass
        return key_points


"""
All camera capture functionality is now handled by the browser frontend
This module only processes frames sent from the client as base64 strings
No OpenCV required - pure MediaPipe + PIL/Pillow for all frame processing
"""
