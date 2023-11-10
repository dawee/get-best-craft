from dataclasses import dataclass, fields
import dataclasses
import requests
from typing import List

def lazy_dataclass_init(instance, **kwargs):
    names = set([f.name for f in fields(instance)])
    for k, v in kwargs.items():
        if k in names:
            setattr(instance, k, v)


@dataclass
class Recipe:
    en: str
    itemId: str

    def __init__(self, **kwargs):
        lazy_dataclass_init(self, **kwargs)


@dataclass
class MarketboardData:
    unitsForSale: int
    unitsSold: int
    averagePrice: float
    currentAveragePrice: int
    recipe: Recipe

    def __init__(self, **kwargs):
        lazy_dataclass_init(self, **kwargs)


def get_alc_recipes():
    res = requests.get('https://api.ffxivteamcraft.com/search?query=&type=Recipe&sort=&sort=desc&filters=clvl%3E=90,clvl%3C=90,craftJob=14&lang=en')
    return [Recipe(**item) for item in res.json()]


def get_mb_infos(recipes: List[Recipe]):
    itemIds = ','.join((str(recipe.itemId) for recipe in recipes))
    res = requests.get(f'https://universalis.app/api/v2/Midgardsormr/{itemIds}')
    json = res.json()

    infos = []
    
    for recipe in recipes:
        if str(recipe.itemId) in json['items']:
            infos.append(MarketboardData(recipe=recipe, **json['items'][str(recipe.itemId)]))

    return infos

mb_infos = get_mb_infos(get_alc_recipes())

# ordered = sorted(mb_infos, key=lambda info: info.averagePrice)
print(sorted(mb_infos, key=lambda info: info.unitsSold * info.currentAveragePrice, reverse=True)[:5])
