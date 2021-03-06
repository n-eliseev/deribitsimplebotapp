# DeribitSimpleBot Example App

Пример рабочего приложения. [Собранного по заданию](https://github.com/n-eliseev/deribitsimplebotapp/blob/master/algalon_developer_test_ru.pdf).\
Приложение использует библиотеку классов описывающих бота ([описание и возможности](https://github.com/n-eliseev/deribitsimplebot)).\
Описание торгового алгоритма есть в задании, а так же на странице [бота](https://github.com/n-eliseev/deribitsimplebot).

## Установка
Клонируйте репозиторий в локальную папку или скачайте архив и распакуйте.

## Настройка перед запуском
Откройте загруженный проект файл docker-compose.yml\
Отредактируйте то что нужно.\
Необходимо указать:
 - client_id - данные из личного кабинета Deribit (раздел настройки API) 
 - client_secret - данные из личного кабинета Deribit (раздел настройки API)

## Запуск
```
docker-compose up
```
После запуска будет создано и запущено два контейнера описанных в файле настройки:
 - **deribit-bot-app** - контейнер в котором будет работать бот. При создании загружает образ, необходимые библиотеки и монтирует приложение из папки app (app.py). Конфиг для работы бота берётся из docker-compose.yml (*секция x-app*)
  - **deribit-bot-mysql** - контейнер с СУБД MySQL, с которой будет работать бот используя базу данных для хранилища логов и данных по ордерам. В образ монтируется папка db/data - которая будет содержать данные базы. В папке data/init-script находится скрипт со структурой БД 