# Бот телеграмма для Игры со временем.

# **INtime!**

## Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.
Примеры сообщений:

<img width="100" alt="2" src="https://github.com/legend233/botforfun/assets/38989679/6201b401-04e9-45b8-9260-70928773654f"> - **1 очко** (зеркало)

<img width="100" alt="2" src="https://github.com/legend233/botforfun/assets/38989679/6201b401-04e9-45b8-9260-70928773654f"> - **2 очка** (двойняшки)

<img width="100" alt="3" src="https://github.com/legend233/botforfun/assets/38989679/ac9e7e7e-cb55-407e-96e5-43223d485051"> - **3 очка** (забор)

<img width="100" alt="4" src="https://github.com/legend233/botforfun/assets/38989679/74ea45c0-4241-4a20-9a1d-673dcf8588e7"> - **4 очка** (флеш рояль)


Игра продолжается до 125 очков. Кто первый достигнет финиша, выйгрывает игру, после чего она заканчивается. Все очки игроков ведуться в рабках одной игры и параллельно ведеться общая статистика.
Есть градации уровней игры. Уровень сменяется, когда игрок набирает 25, 50, 75, 100, 125 очков.

### Список команд:
    /startgame "имя игры" - начать игру
    /endgame "имя игры"  - завершить игру.
    (Необходимо более трех игроков или половина игроков в игре, которые хотят выйти)
    /games - список активных игр
    /connect "имя игры" - подключиться к игре
    /top - показать топ игроков текущей игры
    /total - показать общую статистику игрокам
    /start - помощь

### Важно!
Игроки храняться по их логинам. Если в настройках вашего аккаунта не указан логин, то результат записывается в логин None.

## Запуск бота:

### Console:
    git clone https://github.com/PySofia/botforfun.git
    cd botforfun
    touch .env
    echo "TELEGRAMM_TOKEN=YOUR_TOKEN" >> .env
    echo "DB_PATH=db/sqlite.db" >> .env # или любой другой путь
    pip -r requirements.txt
    python3 main.py

### Docker-CLI:
    
    sudo docker run -d --name botforfun -e "TZ=YOUR TIMEZONE" -e "TELEGRAMM_TOKEN=YOUR_TOKEN" -v "your path to db/sqlite.db:/app/db"  yuchoba/botforfun:latest

### Docker-Compose:
    
    version: '2.2'
    services:
      botforfun:
        image: yuchoba/botforfun:latest
        container_name: botforfun
        restart: unless-stopped
        volumes:
          - YOUR DB DIR:/app/db
        environment:
          - TELEGRAMM_TOKEN=YOUR TOKEN
          - TZ=YOUR TIMEZONE


### ENVs:

- *TELEGRAMM_TOKEN* токен вашего телеграмм бота. Можете получить его от @BotFather. 
- *TZ* - ваш часовой пояс. Например: "Europe/Moscow"

## Благодарности:
Огромное спасибо первым испытателям!
- @Igorikun
- @VladShibanovv
- @LeyliDanilevna
- @RustamNa
- @Lekewka