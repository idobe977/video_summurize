import torch
from faster_whisper import WhisperModel
from moviepy.editor import VideoFileClip
import google.generativeai as genai
from pathlib import Path
import tempfile
from typing import Tuple, Dict
import json
from datetime import datetime
import logging

class MediaProcessor:
    def __init__(self, whisper_model_name: str, gemini_api_key: str, logger: logging.Logger):
        """
        אתחול מעבד המדיה
        
        Args:
            whisper_model_name: שם מודל ה-Whisper לשימוש
            gemini_api_key: מפתח API של Gemini
            logger: מערכת הלוגים
        """
        self.logger = logger
        self.logger.info("מאתחל את מעבד המדיה...")
        
        try:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.logger.info(f"משתמש במכשיר: {self.device}")
            
            self.logger.info(f"טוען מודל Whisper: {whisper_model_name}")
            self.whisper_model = WhisperModel(whisper_model_name, device=self.device)
            
            self.logger.info("מגדיר Gemini API")
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
            
            self.logger.info("אתחול הושלם בהצלחה")
        except Exception as e:
            self.logger.error(f"שגיאה באתחול המודלים: {str(e)}")
            raise
        
    def __del__(self):
        """שחרור משאבים בסיום"""
        self.logger.info("משחרר משאבים...")
        if hasattr(self, 'whisper_model'):
            del self.whisper_model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
    def convert_to_audio(self, video_path: Path, progress_callback=None) -> Path:
        """המרת וידאו לאודיו"""
        self.logger.info(f"ממיר וידאו לאודיו: {video_path}")
        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                self.logger.info(f"יוצר קובץ אודיו זמני: {temp_audio.name}")
                video = VideoFileClip(str(video_path))
                video.audio.write_audiofile(
                    temp_audio.name,
                    logger=None
                )
                video.close()
                
                if progress_callback:
                    progress_callback(1.0, "המרה הושלמה")
                    
                self.logger.info("המרה הושלמה בהצלחה")
                return Path(temp_audio.name)
        except Exception as e:
            self.logger.error(f"שגיאה בהמרת הוידאו: {str(e)}")
            raise
            
    def transcribe_audio(self, audio_path: Path, progress_callback=None) -> str:
        """תמלול קובץ האודיו"""
        self.logger.info(f"מתחיל תמלול: {audio_path}")
        try:
            segments, _ = self.whisper_model.transcribe(str(audio_path), language='he')
            text = ' '.join([seg.text for seg in segments])
            
            if progress_callback:
                progress_callback(1.0, "תמלול הושלם")
                
            self.logger.info(f"תמלול הושלם. אורך הטקסט: {len(text)} תווים")
            return text
        except Exception as e:
            self.logger.error(f"שגיאה בתמלול: {str(e)}")
            raise
            
    def summarize_text(self, text: str, progress_callback=None) -> str:
        """סיכום הטקסט באמצעות Gemini"""
        self.logger.info("מתחיל סיכום טקסט")
        try:
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
                
            self.logger.info(f"סיכום הושלם. אורך הסיכום: {len(summary)} תווים")
            return summary
        except Exception as e:
            self.logger.error(f"שגיאה בסיכום: {str(e)}")
            raise
        
    def save_results(self, transcription: str, summary: str) -> Tuple[str, str]:
        """שמירת התוצאות בפורמטים שונים"""
        self.logger.info("מכין קבצי תוצאות")
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
        
        self.logger.info("הכנת קבצי תוצאות הושלמה")
        return txt_content, json_content
        
    def cleanup(self, *paths: Path) -> None:
        """ניקוי קבצים זמניים"""
        self.logger.info("מנקה קבצים זמניים")
        for path in paths:
            try:
                path.unlink()
                self.logger.info(f"נמחק: {path}")
            except Exception as e:
                self.logger.warning(f"לא הצלחתי למחוק את {path}: {str(e)}") 