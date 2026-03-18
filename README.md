Быстрый старт (Docker)
Клонировать репозиторий:
git clone https://github.com/chocolate1337/testtaskaitiguru.git
cd testtaskaitiguru

контейнеры:
docker-compose up --build -d

сервис доступен по адресу: http://localhost:8000

интерактивная документация (Swagger): http://localhost:8000/docs

тесты:
pytest -v или python -m pytest

Структура проекта
app/api/эндпоинты и роутинг

app/core/ конфигурация (Pydantic Settings) и инициализация БД

app/models/ SQLAlchemy модели

app/schemas/ Pydantic модели (DTO)

app/services/ — Бизнес-логика

tests/ Юнит и интеграционные тесты

Контакты
Автор: Владислав Бысев
Telegram: @sbegato
