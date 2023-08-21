
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  Column, Integer, String
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///sql.db")


class Base(DeclarativeBase): pass
  
class Player(Base):
    __tablename__ = "players"
  
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    score = Column(Integer)

def create_tables():
    # создаем таблицы
    Base.metadata.create_all(bind=engine)


def add_player(name, score):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Person для добавления в бд
        player = Player(name=name, score=score)
        db.add(player)     # добавляем в бд
        db.commit()     # сохраняем изменения

def get_player_score(name):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Person для добавления в бд
        player = db.query(Player).filter(Player.name == name).first()
        return player.score if player else None


def change_player_score(name, score):
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Person для добавления в бд
        player = db.query(Player).filter(Player.name == name).first()
        if player:
            player.score += score
            db.commit()
        else:
            add_player(name, score)


def all_players():
    # создаем сессию подключения к бд
    with Session(autoflush=False, bind=engine) as db:
        # создаем объект Person для добавления в бд
        players = db.query(Player).all()
    dict_players = {}
    for player in players:
        dict_players[player.name] = player.score
    return dict_players



