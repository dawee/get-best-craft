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
    averagePriceHQ: float
    minPriceHQ: float
    hqSaleVelocity: float
    currentAveragePriceHQ: int
    recipe: Recipe
    regularSaleVelocity: float
    unitsForSale: int

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



max_unitsForSale = max(mb_infos, key=lambda info: info.unitsForSale).unitsForSale
min_unitsForSale = min(mb_infos, key=lambda info: info.unitsForSale).unitsForSale

max_hqSaleVelocity = max(mb_infos, key=lambda info: info.hqSaleVelocity).hqSaleVelocity
min_hqSaleVelocity = min(mb_infos, key=lambda info: info.hqSaleVelocity).hqSaleVelocity

max_currentAveragePriceHQ = max(mb_infos, key=lambda info: info.currentAveragePriceHQ).currentAveragePriceHQ
min_currentAveragePriceHQ = min(mb_infos, key=lambda info: info.currentAveragePriceHQ).currentAveragePriceHQ

max_minPriceHQ = max(mb_infos, key=lambda info: info.minPriceHQ).minPriceHQ
min_minPriceHQ = min(mb_infos, key=lambda info: info.minPriceHQ).minPriceHQ


def get_value_rank(value, min_value, max_value):
    return (value - min_value) * 100 / (max_value - min_value)

def get_rank(mbdata: MarketboardData):
    return get_value_rank(mbdata.hqSaleVelocity, min_hqSaleVelocity, max_hqSaleVelocity) * get_value_rank(mbdata.minPriceHQ, min_minPriceHQ, max_minPriceHQ) / max(get_value_rank(mbdata.unitsForSale, min_unitsForSale, max_unitsForSale), 1)

for index, data in enumerate(sorted(mb_infos, key=get_rank, reverse=True)[:10]):
    print(f'{index + 1}: [{data.recipe.itemId}]{data.recipe.en} (minPriceHQ: {data.minPriceHQ}, selling: {data.unitsForSale}, hqSaleVelocity: {data.hqSaleVelocity})')
