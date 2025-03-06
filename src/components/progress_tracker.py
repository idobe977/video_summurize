import streamlit as st
from typing import Optional
from datetime import datetime, timedelta

class ProgressTracker:
    def __init__(self):
        self.progress_bars = {}
        self.start_time = None
        
    def create_progress_bar(self, key: str, description: str) -> None:
        """יצירת סרגל התקדמות חדש"""
        self.progress_bars[key] = {
            "bar": st.progress(0, description),
            "status": st.empty()
        }
        
    def update_progress(self, key: str, progress: float, status: Optional[str] = None) -> None:
        """עדכון ההתקדמות של סרגל ספציפי"""
        if key in self.progress_bars:
            self.progress_bars[key]["bar"].progress(progress)
            if status:
                self.progress_bars[key]["status"].info(status)
                
    def start_tracking(self) -> None:
        """התחלת מעקב זמן"""
        self.start_time = datetime.now()
        
    def get_elapsed_time(self) -> str:
        """קבלת הזמן שעבר מתחילת העיבוד"""
        if not self.start_time:
            return "00:00"
            
        elapsed = datetime.now() - self.start_time
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        return f"{minutes:02d}:{seconds:02d}"
        
    def display_time_estimate(self, file_size_mb: float, has_gpu: bool) -> None:
        """הצגת הערכת זמן לעיבוד"""
        # הערכת זמן גסה בהתבסס על גודל הקובץ ונוכחות GPU
        minutes_per_mb = 0.1 if has_gpu else 0.2
        estimated_minutes = file_size_mb * minutes_per_mb
        
        st.info(
            f"""
            **הערכת זמן עיבוד:**
            - זמן משוער: {estimated_minutes:.1f} דקות
            - מעבד באמצעות: {'GPU' if has_gpu else 'CPU'}
            """
        )
        
    def display_completion(self, success: bool = True) -> None:
        """הצגת סיום העיבוד"""
        if success:
            st.success(
                f"העיבוד הושלם בהצלחה! ⏱️ זמן כולל: {self.get_elapsed_time()}"
            )
        else:
            st.error("אירעה שגיאה במהלך העיבוד") 