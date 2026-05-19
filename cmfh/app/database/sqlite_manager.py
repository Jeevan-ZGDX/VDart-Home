"""SQLite Database Manager for CMFH
Handle user sessions and progress tracking
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path


class SQLiteManager:
    """Manage SQLite database for session storage"""

    def __init__(self, db_path: str = "cmfh_data/cmfh.db"):
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_database()

    def _ensure_db_dir(self):
        """Ensure database directory exists"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_database(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                original_text TEXT,
                rewritten_text TEXT,
                overall_score REAL,
                grammar_score REAL,
                filler_score REAL,
                confidence_score REAL,
                vocabulary_score REAL,
                tedx_score REAL,
                grade TEXT,
                feedback_json TEXT,
                analysis_json TEXT,
                duration_seconds REAL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()
        conn.close()

    def save_session(
        self,
        original_text: str,
        rewritten_text: str,
        scores: Dict[str, Any],
        feedback: Dict[str, Any],
        analysis: Dict[str, Any],
        duration: float = 0.0
    ) -> int:
        """Save a session to database"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sessions (
                created_at, original_text, rewritten_text,
                overall_score, grammar_score, filler_score,
                confidence_score, vocabulary_score, tedx_score,
                grade, feedback_json, analysis_json, duration_seconds
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            original_text,
            rewritten_text,
            scores.get("overall_score"),
            scores.get("grammar_score"),
            scores.get("filler_score"),
            scores.get("confidence_score"),
            scores.get("vocabulary_score"),
            scores.get("tedx_score"),
            scores.get("grade"),
            json.dumps(feedback),
            json.dumps(analysis),
            duration
        ))

        session_id = cursor.lastrowid

        if "filler" in analysis and "filler_ratio" in analysis["filler"]:
            self._save_progress_metric(session_id, "filler_ratio", analysis["filler"]["filler_ratio"])

        if "confidence" in analysis and "confidence_score" in analysis["confidence"]:
            self._save_progress_metric(session_id, "confidence", analysis["confidence"]["confidence_score"])

        if "vocabulary" in analysis and "vocabulary_score" in analysis["vocabulary"]:
            self._save_progress_metric(session_id, "vocabulary", analysis["vocabulary"]["vocabulary_score"])

        conn.commit()
        conn.close()

        return session_id

    def _save_progress_metric(self, session_id: int, metric_name: str, metric_value: float):
        """Save a progress metric"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO user_progress (session_id, metric_name, metric_value, recorded_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, metric_name, metric_value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific session"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        row = cursor.fetchone()

        conn.close()

        if row:
            return dict(row)
        return None

    def get_recent_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sessions"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, created_at, original_text, overall_score, grade, duration_seconds
            FROM sessions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_progress_data(self, metric_name: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get progress data for a specific metric"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT up.metric_value, up.recorded_at, s.id
            FROM user_progress up
            JOIN sessions s ON up.session_id = s.id
            WHERE up.metric_name = ?
            ORDER BY up.recorded_at DESC
            LIMIT ?
        """, (metric_name, limit))

        rows = cursor.fetchall()
        conn.close()

        return [{"value": row["metric_value"], "date": row["recorded_at"], "session_id": row["id"]} for row in rows]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as total FROM sessions")
        total_sessions = cursor.fetchone()["total"]

        if total_sessions > 0:
            cursor.execute("SELECT AVG(overall_score) as avg FROM sessions")
            avg_score = cursor.fetchone()["avg"] or 0

            cursor.execute("SELECT AVG(overall_score) as avg FROM sessions ORDER BY created_at DESC LIMIT 5")
            recent_avg = cursor.fetchone()["avg"] or 0
        else:
            avg_score = 0
            recent_avg = 0

        conn.close()

        return {
            "total_sessions": total_sessions,
            "average_score": round(avg_score, 1),
            "recent_average": round(recent_avg, 1)
        }

    def delete_session(self, session_id: int) -> bool:
        """Delete a session"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_progress WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()

        return deleted

    def clear_all_sessions(self):
        """Clear all sessions (for testing)"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_progress")
        cursor.execute("DELETE FROM sessions")

        conn.commit()
        conn.close()

    def save_setting(self, key: str, value: str):
        """Save a setting"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        """, (key, value))

        conn.commit()
        conn.close()

    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()

        conn.close()

        return row["value"] if row else None