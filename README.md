# praktikum_new_diplom

![Foodgram_Project Workflow Status](https://github.com/danilashishkin/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=master&event=push)



Проект Foodgram собирает отзывы пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка».
Произведению может быть присвоен жанр. Новые жанры может создавать только администратор.
Читатели оставляют к произведениям текстовые отзывы и выставляют произведению рейтинг (оценку в диапазоне от одного до десяти).
Cредняя оценка произведения высчитывается автоматически.

Проект доступен на сервере: 178.154.222.174

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

Выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

Создать суперюзера:

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

## Загрузка базы данными

```
docker-compose exec web python manage.py loaddata fixtures.json
```
## Страница приложения:

```
 http://localhost/admin/

 http://51.250.86.93/redoc/
 http://51.250.86.93/admin/
 http://51.250.86.93/api/v1/
```

## Алгоритм регистрации пользователей
- Пользователь отправляет запрос с параметрами *email* и *username* на */auth/email/*.
- YaMDB отправляет письмо с кодом подтверждения (confirmation_code) на адрес *email* .
- Пользователь отправляет запрос с параметрами *email* и *confirmation_code* на */auth/token/*, в ответе на запрос ему приходит token (JWT-токен).

## Ресурсы API YaMDb

- Ресурс AUTH: аутентификация.
- Ресурс USERS: пользователи.
- Ресурс TITLES: произведения, к которым пишут отзывы (определённый фильм, книга или песня).
- Ресурс CATEGORIES: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
- Ресурс GENRES: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс REVIEWS: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс COMMENTS: комментарии к отзывам. Комментарий привязан к определённому отзыву.

## Документация (запросы для работы с API):

```
 http://localhost/redoc/
```

<<<<<<< HEAD
>**Нельзя добавлять произведения, которые еще не вышли (год выпуска не может быть больше текущего).**
>**При добавлении нового произведения требуется указать уже существующие категорию и жанр.**

=======
>**It is not allowed to add works that have not yet been released (the year of release cannot be greater than the current one).**
>**When adding a new work, you need to specify the already existing category and genre.**
>>>>>>> fe4fad4d8488f5526878f58e5d9020ff2ad76a74
