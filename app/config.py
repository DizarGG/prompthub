"""Единая загрузка настроек для PyCharm, uvicorn и тестовых скриптов."""
import os
from pathlib import Path
from dotenv import load_dotenv

APP_DIR = Path(__file__).resolve().parent
ENV_FILE = APP_DIR / '.env'
# Явный путь не зависит от cwd; для локального проекта .env имеет приоритет.
load_dotenv(dotenv_path=ENV_FILE, override=True)


def setting(name: str, default: str = '') -> str:
    return os.getenv(name, default).strip()


def jwt_secret() -> str:
    value = setting('JWT_SECRET_KEY')
    if len(value) < 32:
        raise RuntimeError(
            f'JWT_SECRET_KEY должен содержать не менее 32 символов. '
            f'Проверьте {ENV_FILE} (файл существует: {ENV_FILE.is_file()}; '
            f'длина загруженного ключа: {len(value)}).'
        )
    return value
