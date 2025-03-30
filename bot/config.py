import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    # Основные настройки
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "")
    
    # База данных
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Настройки администрирования
    ADMIN_ID: Optional[int] = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else None
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Режим разработки
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    @classmethod
    def check_required(cls):
        """Проверка обязательных параметров"""
        errors = []
        required = {
            "BOT_TOKEN": cls.BOT_TOKEN,
            "WEB_APP_URL": cls.WEB_APP_URL
        }
        
        for name, value in required.items():
            if not value:
                errors.append(f"{name} не установлен")
        
        if errors:
            raise EnvironmentError(
                "Ошибка конфигурации:\n- " + "\n- ".join(errors) + 
                "\nПроверьте .env файл или переменные окружения."
            )

config = Config()
