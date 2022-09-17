[![yamdb_workflow](https://github.com/IlyaMashin/yamdb_final/workflows/yamdb_workflow/badge.svg)](https://github.com/IlyaMashin/yamdb_final/actions/workflows/yamdb_workflow.yml)

# Проект YaMDb

***Описание проекта:*** </br>

Проект YaMDb собирает отзывы пользователей на произведения. Произведения деляться на категории: **"Книги", "Фильмы", "Музыка".**

***Установка:***</br>

1.Склонируйте репозиторий в рабочее пространство командной:

```
git clone git@github.com:IlyaMashin/yamdb_final.git
```

2.Установите виртуальное окружение в текущем каталоге командой:

```
python3 -m venv venv
```

3.Активируйте виртуальное окружение и установите все зависимости в соответсвии с подготовленным файлом `requirements.txt`:

```
source venv/bin/activate (for Linux)
source venv/Scripts/activate (for Windows)
pip install -r requirements.txt
```

4.Находясь в текущей дирректории с проектом в папке с файлом `manage.py`, выполните миграции и разверните проект на локальной машине:

```
python manage.py migrate
python manage.py runserver
```

5.Для заполнения базы данных тестовыми данными команда:

```
python manage.py filling_database
```

После успешного запуска сервера будет доступна
[документация проекта](http://localhost/redoc/)

***Используемый стек технологий:***

- Python;
- Django;
- Rest Framework;
- Simple-JWT.

***Разработчики:*** </br>

- [Илья Машин](https://github.com/IlyaMashin/);
