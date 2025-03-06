import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

import streamlit as st
import os
from pathlib import Path
import json
import torch
from components.file_uploader import file_uploader_component
from components.progress_tracker import ProgressTracker
from utils.processor import MediaProcessor

# קונפיגורציה
GEMINI_API_KEY = st.secrets["api_keys"]["gemini"]
MAX_FILE_SIZE_MB = st.secrets["file_settings"]["max_size_mb"]
SUPPORTED_FORMATS = st.secrets["file_settings"]["supported_formats"]
WHISPER_MODEL = st.secrets["models"]["whisper"]

# הגדרות Streamlit
st.set_page_config(
    page_title="מערכת תמלול וסיכום וידאו",
    page_icon="🎥",
    layout="wide"
)

# טעינת CSS מותאם אישית
with open("src/static/css/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def main():
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
        st.error("נא להגדיר מפתח API של Gemini בקובץ .env")
        return
        
    # יצירת מעבד המדיה
    processor = MediaProcessor(WHISPER_MODEL, GEMINI_API_KEY)
    
    # העלאת קובץ
    uploaded_file = file_uploader_component(SUPPORTED_FORMATS, MAX_FILE_SIZE_MB)
    
    if uploaded_file:
        # יצירת עוקב התקדמות
        progress = ProgressTracker()
        
        # הצגת הערכת זמן
        file_size_mb = uploaded_file.stat().st_size / (1024 * 1024)
        progress.display_time_estimate(file_size_mb, torch.cuda.is_available())
        
        if st.button("התחל בעיבוד", key="start_processing"):
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
                
                # ניקוי
                processor.cleanup(uploaded_file, audio_path)
                
            except Exception as e:
                st.error(f"אירעה שגיאה במהלך העיבוד: {str(e)}")
                progress.display_completion(False)

if __name__ == "__main__":
    main() 
