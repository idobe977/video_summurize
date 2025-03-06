import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import streamlit as st
import os
from pathlib import Path
import json
import torch
import psutil
import sys
from components.file_uploader import file_uploader_component
from components.progress_tracker import ProgressTracker
from utils.processor import MediaProcessor
from utils.logger import setup_logger, log_system_info

# הגדרת מערכת הלוגים
logger = setup_logger()
logger.info("=== התחלת ריצת האפליקציה ===")

def check_system_resources():
    """בדיקת משאבי מערכת"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    warnings = []
    
    if memory.available < 4 * 1024 * 1024 * 1024:  # 4GB
        warnings.append("זיכרון פנוי נמוך - מומלץ לפחות 4GB")
    
    if disk.free < 1 * 1024 * 1024 * 1024:  # 1GB
        warnings.append("שטח דיסק פנוי נמוך - מומלץ לפחות 1GB")
        
    return warnings

# יצירת תיקיית temp אם לא קיימת
try:
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    logger.info("תיקיית temp נוצרה בהצלחה")
except Exception as e:
    logger.error(f"שגיאה ביצירת תיקיית temp: {str(e)}")
    st.error(f"שגיאה ביצירת תיקיית temp: {str(e)}")
    sys.exit(1)

# בדיקת הגדרות Streamlit Secrets
try:
    logger.info("טוען הגדרות מערכת...")
    GEMINI_API_KEY = st.secrets["api_keys"]["gemini"]
    MAX_FILE_SIZE_MB = st.secrets["file_settings"]["max_size_mb"]
    SUPPORTED_FORMATS = st.secrets["file_settings"]["supported_formats"]
    WHISPER_MODEL = st.secrets["models"]["whisper"]
    logger.info("הגדרות נטענו בהצלחה")
except Exception as e:
    logger.error(f"שגיאה בטעינת הגדרות: {str(e)}")
    st.error("""
    שגיאה בטעינת הגדרות המערכת. 
    אנא ודא שהגדרת את כל המשתנים הנדרשים ב-Secrets:
    - api_keys.gemini
    - file_settings.max_size_mb
    - file_settings.supported_formats
    - models.whisper
    """)
    st.exception(e)
    sys.exit(1)

# הגדרות Streamlit
st.set_page_config(
    page_title="מערכת תמלול וסיכום וידאו",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# טעינת CSS מותאם אישית
css_path = Path(__file__).parent / "static" / "css" / "style.css"
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        logger.info("קובץ CSS נטען בהצלחה")
else:
    logger.warning("קובץ CSS לא נמצא")
    st.warning("קובץ CSS לא נמצא. חלק מהעיצוב עלול להיות חסר.")

def main():
    try:
        # תיעוד מידע מערכת
        log_system_info(logger)
        
        # בדיקת משאבי מערכת
        system_warnings = check_system_resources()
        if system_warnings:
            for warning in system_warnings:
                logger.warning(warning)
                st.warning(warning)
                
        # כותרת ראשית
        st.markdown(
            """
            <div class="app-header">
                <h1>🎥 מערכת תמלול וסיכום וידאו</h1>
                <p>העלה קובץ וידאו לתמלול וסיכום אוטומטי</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # בדיקת מפתח API
        if not GEMINI_API_KEY:
            logger.error("מפתח API של Gemini לא הוגדר")
            st.error("נא להגדיר מפתח API של Gemini בהגדרות האפליקציה")
            return
            
        # יצירת מעבד המדיה
        try:
            processor = MediaProcessor(WHISPER_MODEL, GEMINI_API_KEY, logger)
        except Exception as e:
            logger.error(f"שגיאה באתחול מעבד המדיה: {str(e)}")
            st.error(f"שגיאה באתחול מעבד המדיה: {str(e)}")
            return
        
        # העלאת קובץ
        try:
            uploaded_file = file_uploader_component(SUPPORTED_FORMATS, MAX_FILE_SIZE_MB)
        except Exception as e:
            logger.error(f"שגיאה בהעלאת הקובץ: {str(e)}")
            st.error(f"שגיאה בהעלאת הקובץ: {str(e)}")
            return
        
        if uploaded_file:
            logger.info(f"קובץ הועלה: {uploaded_file}")
            
            # יצירת עוקב התקדמות
            progress = ProgressTracker()
            
            # הצגת הערכת זמן
            file_size_mb = uploaded_file.stat().st_size / (1024 * 1024)
            logger.info(f"גודל הקובץ: {file_size_mb:.1f}MB")
            progress.display_time_estimate(file_size_mb, torch.cuda.is_available())
            
            if st.button("התחל בעיבוד", key="start_processing"):
                logger.info("התחלת עיבוד הקובץ")
                try:
                    progress.start_tracking()
                    
                    # יצירת סרגלי התקדמות
                    progress.create_progress_bar("convert", "ממיר וידאו לאודיו...")
                    progress.create_progress_bar("transcribe", "מתמלל...")
                    progress.create_progress_bar("summarize", "מסכם...")
                    
                    # המרה לאודיו
                    audio_path = processor.convert_to_audio(
                        uploaded_file,
                        lambda p, s: progress.update_progress("convert", p, s)
                    )
                    
                    # תמלול
                    transcription = processor.transcribe_audio(
                        audio_path,
                        lambda p, s: progress.update_progress("transcribe", p, s)
                    )
                    
                    # סיכום
                    summary = processor.summarize_text(
                        transcription,
                        lambda p, s: progress.update_progress("summarize", p, s)
                    )
                    
                    # הצגת התוצאות
                    st.markdown(
                        """
                        <div class="results-container">
                            <h2>תוצאות העיבוד</h2>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.subheader("📝 תמלול")
                    st.write(transcription)
                    
                    st.subheader("📋 סיכום")
                    st.write(summary)
                    
                    # הכנת קבצים להורדה
                    txt_content, json_content = processor.save_results(transcription, summary)
                    
                    # כפתורי הורדה
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "⬇️ הורד כטקסט",
                            txt_content.encode('utf-8'),
                            "results.txt",
                            "text/plain",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.download_button(
                            "⬇️ הורד כ-JSON",
                            json_content.encode('utf-8'),
                            "results.json",
                            "application/json",
                            use_container_width=True
                        )
                    
                    # הצגת סיום
                    progress.display_completion()
                    logger.info("עיבוד הקובץ הושלם בהצלחה")
                    
                    # ניקוי
                    processor.cleanup(uploaded_file, audio_path)
                    
                except Exception as e:
                    logger.error(f"שגיאה במהלך העיבוד: {str(e)}")
                    st.error(f"אירעה שגיאה במהלך העיבוד: {str(e)}")
                    progress.display_completion(False)

    except Exception as e:
        logger.error(f"שגיאה כללית: {str(e)}")
        st.error(f"שגיאה כללית: {str(e)}")
        st.exception(e)

if __name__ == "__main__":
    main() 