# praktikum_new_diplom

![Foodgram_Project Workflow Status](https://github.com/danilashishkin/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg?branch=master&event=push)



Проект Foodgram это сайт-продуктовый помошник, поможет выбрать рецепт, опубликовать свои рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Проект доступен на сервере: 

http://178.154.222.174/

http://178.154.222.174/admin/

superuser:
```
admin
```
password: 
```
admin
```
email:
```
admin@admin.ru
```
## Стек технологий
- проект написан на Python с использованием Django REST Framework
- библиотека djoser - аутентификация по токенам
- библиотека django-filter - фильтрация запросов
- базы данны - Postgre
- автоматическое развертывание проекта - Docker, docker-compose
- система управления версиями - git
- настроен непрерывный процесс разработки, тестирования и деплоя кода на боевой сервер CI/CD

## Шаблон наполнения env-файла

```
SECRET_KEY=secret_key
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=qwerty
DB_HOST=db
DB_PORT=5432 
```

## Запуск приложения в контейнерах

Выполнить docker-compose:

```
docker-compose up -d
```

Зайти в контейнер и выполнить миграции:

```
sudo docker exec -it foodgram_backend_1 bash
```
```
sudo python manage.py migrate
```

Создать суперюзера:

```
python manage.py createsuperuser
```

Собрать статику:

```
python manage.py collectstatic --no-input
```

Загрузить в базу данные ингредиентов и тегов

```
python manage.py load_data 
```
