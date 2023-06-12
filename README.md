![workflows](https://github.com/MrNavasardyan/foodgram-project-react/blob/master/.github/workflows/main.yml)
# Диплом проект FoodGramm «Продуктовый помощник»
```
http://158.160.65.32
```
## Описание:
```
Сервис позволяет публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список "Избранное", а перед походом в магазин - скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
```
## Технологии:
* Python 3.9
* Django 4.2
* Django REST framework 3.14.0
* Djoser 2.1.0

## Как запустить проект:

### Клонировать репозиторий и перейти в него в командной строке:
* git clone git@github.com:MrNavasardyan/foodgram-project-react.git
* cd foodgram-project-react/

### Переходим в папку с файлом docker-compose.yaml:
* cd infra/

### Создаем файл .env с содержимым:
* DB_ENGINE=django.db.backends.postgresql
* DB_NAME=postgres
* POSTGRES_USER=postgres
* POSTGRES_PASSWORD=postgres
* DB_HOST=db
* DB_PORT=5432

### Установка и запуск приложения в контейнерах:
* docker-compose up -d

### Запускаем миграций, создаём суперпользователя, сбор статики и заполнение БД:
* docker-compose exec web python manage.py migrate
* docker-compose exec web python manage.py createsuperuser
* docker compose exec web python manage.py loaddata new_ingredients.json
* docker-compose exec web python manage.py collectstatic --no-input
* docker compose cp ../data/new_ingredients.json web:/app
* docker compose web exec python manage.py loaddata new_ingredients.json
## Документация к API:
Полная документация прокта (redoc) доступна по адресу http://158.160.65.32/api/docs/redoc.html
###
Панель администратора
http://158.160.65.32/admin/
admin/admin
.