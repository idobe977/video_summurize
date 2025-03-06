import streamlit as st
from pathlib import Path
import os
from typing import List, Optional

def file_uploader_component(
    supported_formats: List[str],
    max_size_mb: int
) -> Optional[Path]:
    """
    קומפוננטה מעוצבת להעלאת קבצים
    
    Args:
        supported_formats: רשימת הפורמטים הנתמכים
        max_size_mb: גודל מקסימלי בMB
    
    Returns:
        Path של הקובץ שהועלה או None אם לא הועלה קובץ
    """
    
    st.markdown(
        """
        <div class="upload-container">
            <h3>העלה קובץ וידאו לתמלול</h3>
            <p>גרור קובץ לכאן או לחץ לבחירה</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_file = st.file_uploader(
        "העלה קובץ",
        type=supported_formats,
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        if file_size_mb > max_size_mb:
            st.error(
                f"הקובץ גדול מדי! הגודל המקסימלי המותר הוא {max_size_mb}MB"
            )
            return None
            
        # שמירת הקובץ באופן זמני
        temp_dir = Path("temp")
        temp_dir.mkdir(exist_ok=True)
        
        temp_path = temp_dir / uploaded_file.name
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return temp_path
        
    return None 