"""Запуск: python -m app.test_config_ollama (из папки над app)."""
import time
from app.config import ENV_FILE, jwt_secret, setting
from app.AI.client import AICL

print('Файл настроек:', ENV_FILE, '| существует:', ENV_FILE.is_file())
try:
    print('JWT_SECRET_KEY: OK, длина:', len(jwt_secret()))
except RuntimeError as exc:
    print('JWT_SECRET_KEY:', exc)
print('OLLAMA_HOST:', setting('OLLAMA_HOST', 'http://127.0.0.1:11434'))
print('OLLAMA_MODEL:', setting('OLLAMA_MODEL', 'qwen3:4b'))
start = time.monotonic()
try:
    result = AICL().generate_text('Составь краткий промпт для изучения Python')
    print('Ответ Qwen:', result)
except Exception as exc:
    print('Ошибка Ollama:', type(exc).__name__, str(exc))
finally:
    print('Продолжительность:', round(time.monotonic() - start, 2), 'с')
