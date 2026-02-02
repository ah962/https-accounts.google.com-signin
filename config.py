import os
from datetime import timedelta

class Config:
    # مفتاح سري لتوقيع الجلسات
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-12345'
    
    # قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///auth_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات الجلسة
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # إعدادات الأمان
    SESSION_COOKIE_SECURE = False  # True في الإنتاج
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # رفع الملفات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
