# Бот телеграмма для Игры со временем.

# **INtime!**

## Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.
Примеры сообщений:

    10:01 - 1 очко - (зеркало)
    10:10 - 2 очка - (двойняшки)
    11:11 - 3 очка - (забор)
    12:34 - 4 очка - (флеш рояль)

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