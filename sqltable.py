
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import Session
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
engine = create_engine("sqlite:///" + os.getenv('DB_PATH'))
DEV_MODE = os.getenv('DEV_MODE')

class Base(DeclarativeBase): pass
  
class Player(Base):
    __tablename__ = "players"
  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    game_name = Column(String, ForeignKey('games.game_name'))
    score = Column(Integer)
    play_status = Column(Boolean, default=True)

class Games(Base):
    __tablename__ = "games"
  
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(String)
    game_name = Column(String)
    online_status = Column(Boolean, default=True)



def create_tables():
    # создаем таблицы
    Base.metadata.create_all(bind=engine)


def get_player_score(id, name):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        game_name = db.query(Games).filter(Games.chat_id == id, Games.online_status == True).first()
        if game_name:
            game_name = game_name.game_name
            # создаем запрос к Player в бд
            player = db.query(Player).filter(Player.game_name == game_name, Player.name == name).first()
            return player.score if player else 0
        else:
            return 0

def get_game(id):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        game = db.query(Games).filter(Games.chat_id == id, Games.online_status == True).first()
        if game:
            return game.game_name, game.online_status


def change_player_score(id, name, score):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        game_name = db.query(Games).filter(Games.chat_id == id, Games.online_status == True).first()
        if game_name:
            game_name = game_name.game_name
            # Меняем значение score для Player или создаем объект Player для добавления в бд
            player = db.query(Player).filter(Player.name == name, Player.game_name == game_name, Player.play_status == True).first()
            if player:
                player.score += score
            else:
                player = Player(name=name, score=score, game_name=game_name)
                db.add(player)
        
            db.commit() # добавляем в бд


def all_players(chat_id):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Player для добавления в бд
        game_name = db.query(Games).filter(Games.chat_id == chat_id, Games.online_status == True).first()
        if game_name:
            game_name = game_name.game_name
            players = db.query(Player).filter(Player.game_name == game_name).all()
            dict_players = {}
            for player in players:
                dict_players[player.name] = player.score
        else:
            dict_players = {}
        return dict_players

def player_status_change(game_name: str, name: str):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Player для изменения в бд
        player = db.query(Player).filter(Player.name == name, Player.game_name == game_name).first()
        if player:
            player.play_status = False
            db.commit()
            players_status = db.query(Player.name, Player.play_status).filter(Player.game_name == game_name).all()
        else:
            players_status = []
        return players_status

def all_games():
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для добавления в бд
        games = db.query(Games.game_name).all()
    return [x[0] for x in games]

def all_games_online():
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для добавления в бд
        games = db.query(Games.game_name).filter(Games.online_status == True).all()
    return list(set([x[0] for x in games]))

def add_game(id, name):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для добавления в бд
        game = Games(chat_id=id, game_name=name)
        db.add(game)     # добавляем в бд
        db.commit()     # сохраняем изменения


def game_status_change(id):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для изменения в бд
        game_name = db.query(Games).filter(Games.chat_id == id, Games.online_status == True).first()
        games = db.query(Games).filter(Games.game_name == game_name.game_name).all()
        for game in games:
            game.online_status = False
        players = db.query(Player).filter(Player.game_name == game_name.game_name).all()
        for player in players:
            player.play_status = False
        db.commit()     # сохраняем изменения


def game_status_check(id):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для изменения в бд
        game = db.query(Games).filter(Games.chat_id == id, Games.online_status == True).first()
        return game

def total_players():
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Game для изменения в бд
        players = db.query(Player).all()
        scores = dict()
        for player in players:
            if scores.get(player.name):
                scores[player.name] += player.score
            else:
                scores[player.name] = player.score
    return scores

if not os.path.exists(os.getenv('DB_PATH')):
    create_tables()