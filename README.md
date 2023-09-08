# botforfun

# Бот телеграмма для игры со временем.

## Правила
Игроки должны написать в сообщении красивое время в это самое время. За попадание в то самое время начисляются очки.

Примеры сообщений:
- 10:01 - 1 очко - (симетрия)
- 10:10 - 2 очка - (зеркало)
- 11:11 - 3 очка - (забор)
- 12:34 - 4 очка - (флеш рояль)

## Команды
- /top - показывает список игроков и их суммарные очки
- /game_start - начинает игру
- /game_end - завершает игру
- /time - показывает текущее время
- /total - показывает общее количество очков во всех играх за все время
- /help - показывает список команд и правила

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