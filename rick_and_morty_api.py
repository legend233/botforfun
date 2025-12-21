import requests
import json
import random


HOST = "https://rickandmortyapi.com/api"


class RickAndMortyAPI:
    def __init__(self):
        self.characters = f"{HOST}/character"
        self.locations = f"{HOST}/location"
        self.episodes = f"{HOST}/episode"
            
    def _get(self, url, params=None):
        response = requests.get(url, params=params)
        return response
    
    def get_characters(self, id=None, name=None, gender=None):
        if id is None:
            url = f"{self.characters}"
        else:
            url = f"{self.characters}/{id}"
        return self._get(url, params={"id": id, "name": name, "gender": gender}).json()
    
    def get_count_characters(self):
        response = self._get(f"{self.characters}")
        count = response.json().get("info").get("count")
        return count

    def get_rundom_character(self) -> tuple[str, bytes]:
        """Возвращает рандомного персонажа. информацию и картинку в байтах"""
        full_count = self.get_count_characters()
        response = self.get_characters(id=random.randint(1, full_count))
        image = self._get(response.get("image")).content
        episode = self._get(response.get("episode")[-1]).json()
        episode_num = episode.get("episode")
        episode_name = episode.get("name")
        message = "Ты персонаж мультсериала: Рик и Морти\n" \
                  f"Твое имя: {response.get('name')}\n" \
                  f"Твой статус: {response.get('status')}\n" \
                  f"Твой пол: {response.get('gender')}\n" \
                  f"Твоя раса: {response.get('species')}\n" \
                  f"Твоя локация: {response.get('location').get('name')}\n" \
                  f"Тебя видели в последний раз в эпизоде {episode_num}: '{episode_name}'"
        return message, image


if __name__ == "__main__":
    api = RickAndMortyAPI()
    full_count = api.get_count_characters()
    print("Всего персонажей:", full_count)
    response = api.get_characters(id=random.randint(1, full_count))
    print(response)
