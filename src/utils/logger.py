import logging
from pathlib import Path
import sys
import psutil
import torch
from datetime import datetime

def setup_logger():
    """הגדרת מערכת הלוגים"""
    # יצירת תיקיית לוגים
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # הגדרת שם קובץ הלוג עם תאריך ושעה
    log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # הגדרת פורמט הלוג
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # הגדרת handler לקובץ
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # הגדרת handler למסוף
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    
    # הגדרת הלוגר
    logger = logging.getLogger('VideoProcessor')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger

def log_system_info(logger):
    """תיעוד מידע על המערכת"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logger.info("=== מידע מערכת ===")
    logger.info(f"מעבד: {psutil.cpu_count()} ליבות")
    logger.info(f"זיכרון כולל: {memory.total / (1024**3):.1f}GB")
    logger.info(f"זיכרון פנוי: {memory.available / (1024**3):.1f}GB")
    logger.info(f"שטח דיסק פנוי: {disk.free / (1024**3):.1f}GB")
    logger.info(f"GPU זמין: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        logger.info(f"דגם GPU: {torch.cuda.get_device_name()}")
    logger.info("===================") 