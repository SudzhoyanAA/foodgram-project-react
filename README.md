### Описание проекта 
«Фудграм» — сайт, на котором пользователи публикуют рецепты, добавляют 
чужие рецепты в избранное и подписываются на публикации других авторов. 
Пользователям сайта также доступен сервис «Список покупок». 
Он позволяет создавать список продуктов, которые нужно купить для приготовления 
выбранных блюд.

## Установка 
1. Клонируйте репозиторий на свой компьютер:
```bash
git clone git clone <https or SSH URL>
```

Перейти в каталог проекта:
```bash
cd foodgram
```

Создать .env:
```bash
touch .env
```

Шаблон содержимого для .env файла:
```bash
# Django settings
DEBUG=False
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=127.0.0.1;localhost;<example.com;xxx.xxx.xxx.xxx>

# DB
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
```

Развернуть приложение:

```bash
docker compose -f docker-compose.dev.yml up -d
```
Выполнить заполнение базы ингредиентами:
```bash
docker compose exec backend python manage.py load_data_csv
```

## Запуск проекта на удаленном сервере

Инструкция предполагает, что удаленный сервер настроен на работу по SSH. 
На сервере установлен Docker. 
Установлен и настроен nginx в качестве балансировщика нагрузки.

Для развертывания на удаленном сервере необходимо клонировать репозиторий на 
локальную машину. Подготовить и загрузить образы на Docker Hub.

Клонировать репозиторий:
```shell
git clone git clone <https or SSH URL>
```

Перейти в каталог проекта:
```shell
cd foodgram
```

Создать .env:
```shell
touch .env
```

Шаблон содержимого для .env файла:
```shell
# Django settings
DEBUG=False
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=127.0.0.1;localhost;<example.com;xxx.xxx.xxx.xxx>

# DB
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=django
DB_HOST=db
DB_PORT=5432
```

Создать docker images образы:
```shell
sudo docker build -t <username>/food_back backend/foodgram
sudo docker build -t <username>/food_front frontend/
sudo docker build -t <username>/food_gateway gateway/
```

Загрузить образы на Docker Hub:
```shell
sudo docker push <username>/food_back
sudo docker push <username>/food_front
sudo docker push <username>/food_gateway
```

Создать на сервере папку `foodgram` 
```shell
mkdir /home/<username>/foodgram
```

Перенести на удаленный сервер файлы`.env` и `docker-compose.prod.yml`.
```shell
scp .env docker-compose.prod.yml <username>@<server_address>:/home/<username>/foodgram
```

Подключиться к серверу:
```shell
ssh <username>@<server_address>
```

Перейти в директорию `foodgram`:
```shell
cd /home/<username>/foodgram
```

Выполнить сборку приложений:
```shell
sudo docker compose -f docker-compose.production.yml up -d
```

Выполните миграции, соберите статические файлы бэкенда и скопируйте их в /static/static/:

```bash
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

Измените настройки location в секции server:

```bash
location / {
    proxy_set_header Host $http_host;
    proxy_pass http://127.0.0.1:9000;
}
```

Проверьте работоспособность конфига Nginx:

```bash
sudo nginx -t
```
Если ответ в терминале такой, значит, ошибок нет:
```bash
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

Перезапускаем Nginx
```bash
sudo service nginx reload
```

## GitHub Actions
Для использования автоматизированного развертывания и тестирования нужно 
изменить `.github/workflows/main.yml` под свои параметры и задать Actions secrets
в репозитории.

Actions secrets:
- `secrets.DOCKER_USERNAME`
- `secrets.DOCKER_PASSWORD`
- `secrets.HOST`
- `secrets.USER`
- `secrets.SSH_KEY`
- `secrets.SSH_PASSPHRASE`
- `secrets.TELEGRAM_TO`
- `secrets.TELEGRAM_TOKEN`

## Примеры запросов к API.
Получение списка рецептов:
GET /api/recipes/
```bash
{
  "count": 123,
  "next": "http://127.0.0.1:8081/api/recipes/?page=2",
  "previous": "http://127.0.0.1:8081/api/recipes/?page=1",
  "results": [
    {
      "id": 0,
      "tags": [
        {
          "id": 0,
          "name": "Завтрак",
          "color": "green",
          "slug": "breakfast"
        }
      ],
      "author": {
        "email": "root@root.ru",
        "id": 0,
        "username": "Albert",
        "first_name": "Albert",
        "last_name": "Sudzhoyan",
        "is_subscribed": false
      },
      "ingredients": [
        {
          "id": 0,
          "name": "Курица",
          "measurement_unit": "г",
          "amount": 100
        }
      ],
      "is_favorited": false,
      "is_in_shopping_cart": false,
      "name": "string",
      "image": "https://backend:8081/media/recipes/images/image.jpeg",
      "text": "string",
      "cooking_time": 10
    }
  ]
}
```
Регистрация пользователя:
POST /api/users/
```bash
{
  "email": "root@root.ru",
  "username": "Albert",
  "first_name": "Albert",
  "last_name": "Sudzhoyan",
  "password": "******"
}
```
Подписаться на пользователя:
POST /api/users/{id}/subscribe/ 
```bash
{
  "email": "root@root.com",
  "id": 0,
  "username": "Albert",
  "first_name": "Albert",
  "last_name": "Sudzhoyan",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "https://backend:8081/media/recipes/images/image.jpeg",
      "cooking_time": 10
    }
  ],
  "recipes_count": 1
}
```
## Автор и доступ.
Автор - Albert
Доступ к админ панели:
login: root@root.ru
password: 123456

## Используемые технологии.
- [![Python](https://img.shields.io/badge/Python-3.8-blue.svg)](https://www.python.org/)
- [![Django](https://img.shields.io/badge/Django-3.2-green.svg)](https://www.djangoproject.com/)
- [![Nginx](https://img.shields.io/badge/Nginx-latest-brightgreen.svg)](https://nginx.org/)
- [![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12.0-blue.svg)](https://www.postgresql.org/)