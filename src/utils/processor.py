import torch
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
import google.generativeai as genai
from pathlib import Path
import tempfile
from typing import Tuple, Dict
import json
from datetime import datetime

class MediaProcessor:
    def __init__(self, whisper_model_name: str, gemini_api_key: str):
        """
        אתחול מעבד המדיה
        
        Args:
            whisper_model_name: שם מודל ה-Whisper לשימוש
            gemini_api_key: מפתח API של Gemini
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.whisper_model = WhisperModel(whisper_model_name, device=self.device)
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
    def convert_to_audio(self, video_path: Path, progress_callback=None) -> Path:
        """המרת וידאו לאודיו"""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
            video = VideoFileClip(str(video_path))
            video.audio.write_audiofile(
                temp_audio.name,
                logger=None
            )
            video.close()
            
            if progress_callback:
                progress_callback(1.0, "המרה הושלמה")
                
            return Path(temp_audio.name)
            
    def transcribe_audio(self, audio_path: Path, progress_callback=None) -> str:
        """תמלול קובץ האודיו"""
        segments, _ = self.whisper_model.transcribe(str(audio_path), language='he')
        text = ' '.join([seg.text for seg in segments])
        
        if progress_callback:
            progress_callback(1.0, "תמלול הושלם")
            
        return text
        
    def summarize_text(self, text: str, progress_callback=None) -> str:
        """סיכום הטקסט באמצעות Gemini"""
        prompt = f"""אנא סכם את הטקסט הבא בצורה תמציתית ומובנת:
        
        {text}
        
        הסיכום צריך להיות:
        1. ברור ותמציתי
        2. מכיל את הנקודות העיקריות
        3. מאורגן בצורה לוגית
        """
        
        response = self.gemini_model.generate_content(prompt)
        summary = response.text
        
        if progress_callback:
            progress_callback(1.0, "סיכום הושלם")
            
        return summary
        
    def save_results(self, transcription: str, summary: str) -> Tuple[str, str]:
        """שמירת התוצאות בפורמטים שונים"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # יצירת תוכן טקסט
        txt_content = f"""תאריך ושעה: {timestamp}

תמלול:
{transcription}

סיכום:
{summary}"""

        # יצירת תוכן JSON
        json_content = json.dumps({
            "timestamp": timestamp,
            "transcription": transcription,
            "summary": summary
        }, ensure_ascii=False, indent=2)
        
        return txt_content, json_content
        
    def cleanup(self, *paths: Path) -> None:
        """ניקוי קבצים זמניים"""
        for path in paths:
            try:
                path.unlink()
            except Exception:
                pass 