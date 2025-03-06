# 🎥 מערכת תמלול וסיכום וידאו

מערכת לתמלול אוטומטי של קבצי וידאו וסיכום התוכן באמצעות AI.

## ✨ תכונות

- 🎬 תמיכה במגוון פורמטים של וידאו
- 🔊 המרה אוטומטית לאודיו
- 📝 תמלול באמצעות Faster-Whisper
- 📋 סיכום חכם באמצעות Gemini
- 💫 ממשק משתמש מודרני ונוח
- ⬇️ ייצוא תוצאות ב-TXT ו-JSON

## 🚀 התקנה

1. התקן את הדרישות:
```bash
pip install -r requirements.txt
```

2. צור קובץ `.env` והגדר את המשתנים הבאים:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MAX_FILE_SIZE_MB=200
SUPPORTED_VIDEO_FORMATS=["mp4", "avi", "mov", "mkv"]
WHISPER_MODEL=ivrit-ai/faster-whisper-v2-d4
```

## 🎯 שימוש

הרץ את האפליקציה:
```bash
streamlit run src/app.py
```

## 📋 דרישות מערכת

- Python 3.8+
- 8GB RAM לפחות
- מעבד חזק או GPU (מומלץ)
- דיסק מהיר לעיבוד הקבצים

## 🔑 מפתחות API

- נדרש מפתח API של Gemini. ניתן להשיג [כאן](https://makersuite.google.com/app/apikey).

## 📝 רישיון

MIT License 