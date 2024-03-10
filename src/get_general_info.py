import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
from src.get_companies import get_bist100
from src.get_companies import get_bist_companies


def get_general_info(ticker,online=False) :
    with open('bist100.json','r',encoding='utf-8' ) as b:
        bist = json.load(b)
    with open('bist_companies_info.json','r',encoding='utf-8' ) as f:
        c = json.load(f)
    if online:
        c = get_bist_companies(output='dict')
        bist = get_bist100()

    if (ticker in  bist) :
        return list(filter(lambda x : x['company'] in [ticker], c))[0]
    else:
        return print('BIST 100 sirketi girin')