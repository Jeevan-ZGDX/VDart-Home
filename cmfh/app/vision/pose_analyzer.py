"""Vision Module for CMFH
Real-time pose detection and body language analysis using MediaPipe
"""

import cv2
import numpy as np
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

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a single frame for pose"""
        self._load_media_pipe()

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self._pose.process(rgb_frame)

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
            right_elbow = namespaces[14]

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
            right_elbow = namespaces[14]
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


class CameraHandler:
    """Handle camera input and processing"""

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self._cap = None
        self._pose_analyzer = PoseAnalyzer()
        self._is_running = False

    def start(self) -> bool:
        """Start camera"""
        try:
            self._cap = cv2.VideoCapture(self.camera_id)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return self._cap.isOpened()
        except Exception as e:
            print(f"Camera error: {e}")
            return False

    def get_frame(self) -> Optional[np.ndarray]:
        """Get next frame"""
        if self._cap and self._cap.isOpened():
            ret, frame = self._cap.read()
            if ret:
                return frame
        return None

    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze frame"""
        return self._pose_analyzer.analyze_frame(frame)

    def stop(self):
        """Stop camera"""
        self._is_running = False
        if self._cap:
            self._cap.release()


def draw_pose_overlay(frame: np.ndarray, analysis: Dict[str, Any]) -> np.ndarray:
    """Draw pose analysis overlay on frame"""
    if not analysis.get("detected", False):
        return frame

    overlay = frame.copy()

    h, w = frame.shape[:2]

    cv2.putText(overlay, f"Posture: {analysis.get('posture_score', 0)}%", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(overlay, f"Hands: {analysis.get('hand_gesture', 'N/A')}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(overlay, f"Arms: {analysis.get('arm_position', 'N/A')}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(overlay, f"Confidence: {analysis.get('confidence_level', 'N/A')}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    suggestions = analysis.get("suggestions", [])
    for i, suggestion in enumerate(suggestions[:3]):
        cv2.putText(overlay, f"Tip: {suggestion[:50]}...", (10, 160 + i * 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

    return overlay