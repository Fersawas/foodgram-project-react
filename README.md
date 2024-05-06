# FOODGRAM
## Описание проекта
Проект foodgram позволяет создавать "рецепты". Рецепт состоит из ингредиентов, наименования, картинки, описания, все поля редактируемы.
### Содержанеие

- [Технологии](#tech)
- [Начало работы](#begining)
- [Запуск через docker](#docker)
- [FAQ](#faq)
- [Комнада проекта](#team)

## <a name="tech">Технологии</a>

- [Django](https://www.djangoproject.com/)
- [Django REST](https://www.django-rest-framework.org/)
- [Docker](https://www.docker.com/)

## <a name="begining">Начало работы</a>

### Начало работы

Активируйте вирутальное окржуние:

```
python -m venv venv
```

### Установка зависимостей

Установите зависимости из файла *requirements.txt*:

```
pip install -r requirements.txt
```

Если вы работаете локально, в файле .env установите:
*.env*
```
TEST_DATABASE = TRUE
```

### Установка зависимостей

Активируйте виртуальное окружение

```
source venv/sqripts/activate
```

Применение миграций и первый запуск:

```
python manage.py migrate
```

Заполняем базу данных

```
python manage.py csv_to_sql
```

### Запуск сервера

Запустите проект:

```
python manage.py runserver
```

## <a name="docker">Запуск через docker</a>

Зайти в корневую директорию. 
Запустить docker файл:

```
docker compose -f docker-compose.yml up -d
```

Соберите и скопируйте статику

```
docker compose -f docker-compose.yml exec backend python manage.py collect_static
docker compose -f docker-compose.yml exec backend cp -r /app/static/. /backend_static/static/ 
```

Примение миграции и заполните базу данных

```
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py csv_to_sql
```

Ваш сайт доступен по адресу /localhost:8080/

Если захотите отключить локальный сервер
Введите следующие команды

```
docker compose -f docker-compose.yml down -v
```

## <a name="faq">FAQ</a>

### Могу ли я добавлять рецепты?

Да, вы можете

### А оно работает?

Еще 30 дней!!

### А редактировать профиль можно?

Нет

## <a name="team">Команда проектка</a>

- Паршин Денис - backend developer
- Максим Болотских - ревьювер