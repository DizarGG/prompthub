# PromptHub — учебное хранилище промптов

Сохранена структура ученика: `AI/`, `authorization/`, `datasourse/`, `domain/`, `web/` и `main.py`. Название `datasourse` оставлено для совместимости, хотя правильнее `datasource`.

## Первый запуск

1. Python 3.11+; установите PostgreSQL и Ollama.
2. Создайте БД, например через `psql -U postgres -c "CREATE DATABASE prompt_storage;"` (при необходимости задайте хост/порт).
3. Из папки **над** `app` выполните:
   ```bash
   python -m venv .venv
   # Linux/macOS: source .venv/bin/activate
   # Windows PowerShell: .venv\\Scripts\\Activate.ps1
   pip install -r app/requirements.txt
   ```
4. Скопируйте `app/.env.example` в `app/.env`, настройте `DATABASE_URL`, замените `JWT_SECRET_KEY` на случайный секрет длиной >=32 символов. Можно сгенерировать командой `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
5. Загрузите модель: `ollama pull qwen3:4b`. Запустите Ollama (`ollama serve`, если служба ещё не запущена).
6. Из **родительской папки** выполните `uvicorn app.main:app --reload`.
7. Откройте http://localhost:8000/ (страница) и http://localhost:8000/docs (Swagger UI).

Для отдельного фронтенда можно открыть `app/frontend/index.html` через Live Server на `http://localhost:5500`. Переменная `API_BASE` расположена в начале JS-секции (под стилями). В случае другого порта измените также `CORS_ORIGINS` в `.env` и перезапустите сервер. Не открывайте файл через `file://`.

## API

- `POST /users`: JSON `{ "username": "student", "email": "student@example.com", "password": "pass12345" }`.
- `POST /login`: **form-urlencoded** `username=student&password=pass12345` → JWT.
- `GET /protected/profile`: JWT.
- `POST /AI/generate`: JSON `{ "promt": "Составь план обучения Python" }` → `{ "promt": "..." }`. Старое имя `promt` оставлено ради совместимости.
- `GET /projects?q=&skip=0&limit=20`: общедоступные промпты.
- `GET /projects/{id}`: конкретный промпт.
- `POST /projects`: JWT + JSON `{ "title": "...", "description": "...", "content": "..." }`.
- `DELETE /projects/{id}`: JWT; удалять может только автор.

Список пользователей пока общедоступен как в исходном учебном проекте; в публичном продукте лучше убрать/ограничить эти маршруты. Пароли никогда не возвращаются API.

## Важно при переходе с исходной версии

`create_all()` создаёт только отсутствующие таблицы и **не мигрирует** уже существующие. Если данные в старой PostgreSQL БД нужны, сначала сделайте бэкап и миграцию Alembic; не удаляйте таблицы. Старые пользовательские пароли в открытом виде несовместимы с новым Argon2-хешированием — нужны сброс паролей или безопасная миграция. Исходный архив содержал настоящий пароль к PostgreSQL: смените его в самой БД. В `.env.example` стоят только демонстрационные значения.

Для обучения оставлена синхронная SQLAlchemy и простой `create_all` при старте. Следующие этапы: Alembic, полноценные тесты с отдельной БД, лимит запросов генерации, роли и модерация публичных промптов, хранение версии модели, контроль длины ответа Ollama, редактирование промптов, logout/отзыв JWT. Tailwind CDN подходит для учебного прототипа, не для production.
