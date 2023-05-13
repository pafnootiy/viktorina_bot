 # Бот Викторина для Telegram и VK Groups


## Установка и настройка

 

Для тестирования Вы можете использовать ботов в TG: https://t.me/fd_dev_bot или в VK : https://vk.com/event41445255

## Подготовка к запуску

Для запуска сайта вам понадобится Python 3.0 и выше.

Скачайте код с GitHub. 

Установите вириуальное окружение в репозиторий

```sh
python -m venv venv
```
Активируйте его 
```sh
python venv/Scripts/activate
```
Установите зависимости:
```sh
pip install -r requirements.txt
```
## Добавьте переменные окружения 
Создайте файл .env со следующими переменными, где:

* TG_API_TOKEN=токен телеграмм бота  
* PROGECT_ID= ID проекта из json файла с ключами.  
* DIALOG_FLOW_TOKEN = токен для DialogFlow 
* TG_CHAT_ID= чат id в телеграмме. 
* VK_TOKEN = токен группы в VK
* REDIS_PASS = пароль для Redis

Пример записи в файле .env

* TG_API_TOKEN=5969555759:AAFTmoRUfTq_ZHPPb0Ra0ulY3RtLvTwJ1mg
* PROGECT_ID=dvmn-project-gwll
* GOOGLE_APPLICATION_CREDENTIALS='C:\Users\Alex K\AppData\Roaming\gcloud\application_default_credentials.json'
* REDIS_PASS = 5tliTKK645CuuMA4qtMvBIQvKF4XkVga
* TG_CHAT_ID=230938172
* VK_TOKEN = vk1.a.QD-ChVpJV3HBTTmJJwtE5nDGA0VZkL82-0UWrDmTAwD9lYrw5XrCyFsro1ZiY8DXCZnUcKuwx-iE4CJE1H-fc-CMcCBVUu5e93xlT4nKdbjDUVaJ0OeqifkNzo3YZZkW2ggYPbhFnx7f4u3VEUZ-e-zDr4L-TmvNPzYBvOgmrO4b7OVyHW5SVXPdB1Z4gKCqsxcU6cSHnK7PSrbd3xTtUQ

## Запуск 
Для запуска бота в консоли введите следующие команды 

```sh
python tg_bot.py
```
```sh
python vk_bot.py
```


### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков Devman
