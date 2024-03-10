import requests
import json
from bs4 import BeautifulSoup
import regex as re
import pandas as pd
from datetime import datetime,timedelta
import os

def extract_ticker_name(ticker):
    return ticker.split(',')[0].strip()  


def convert_time(time_str):
    if  time_str.startswith("Dün"):  
        time_str = time_str.replace("Dün ", "")
        time_format = "%H:%M"  
        yesterday = datetime.today() - timedelta(days=1)
        time = datetime.strptime(time_str, time_format).time()
        return datetime.combine(yesterday, time)
    elif time_str.startswith("Bugün"):
        time_str = time_str.replace("Bugün ","")
        time_format = "%H:%M"
        today = datetime.today()
        time = datetime.strptime(time_str,time_format).time()
        return datetime.combine(today,time)
    else:
        return datetime.strptime(time_str, "%d.%m.%y %H:%M")
    

def get_announce(fromdate = datetime.today().date() - timedelta(days = 3), todate=datetime.today().date()):

    company_ids = []
    with open('bist_companies_info.json','r',encoding='utf-8' ) as f:
        c = json.load(f)
        for company in c :
            if company['company_index'] is not None:
                company_ids.append(company['company_id'])
    
    data = {
            "fromDate": str(fromdate),
            "toDate": str(todate),
            "year": "", "prd": "",
            "term": "", "ruleType": "",
            "bdkReview": "",
            "disclosureClass": "",
            "index": "", "market": "",
            "isLate": "", "subjectList":[],
            "mkkMemberOidList": company_ids,
            "inactiveMkkMemberOidList": [],
            "bdkMemberOidList": [],
            "mainSector": "", "sector": "",
            "subSector": "", "memberType": "IGS",
            "fromSrc": "N", "srcCategory": "",
            "discIndex": []}
    response = requests.post(url="https://www.kap.org.tr/tr/api/memberDisclosureQuery", json=data)
    disclosures=response.json()

    details=[]
    for item in disclosures:
        if 'stockCodes' in item:
            detail = {
                #'company_id':item['mkkMemberOidList'],
                'ticker':extract_ticker_name(item['stockCodes']),
                'name':item['kapTitle'],
                'time':convert_time(time_str=item['publishDate']).strftime("%Y-%m-%d %H:%M:%S"),
                'class':item['disclosureClass'],
                'disc_index':item['disclosureIndex']
            }
            details.append(detail)
        
    if os.path.exists('announcement.json'):   
        with open('announcement.json', 'r', encoding='utf8') as f:
            existing_data = json.load(f)
            new_detail_list=[]
            for new_detail in details:
                #veri çiftleme kontrol
                if not any(existing_detail['name'] == new_detail['name'] and existing_detail['time']==new_detail['time'] for existing_detail in existing_data):
                    existing_data.append(new_detail)
                    new_detail_list.append(new_detail)
            details = existing_data

    with open('announcement.json', 'w', encoding='utf8') as f:
        json.dump(details, f, ensure_ascii=False, indent=4)
    with open('new_announcement.json', 'w', encoding='utf8') as f:
        json.dump(new_detail_list, f, ensure_ascii=False, indent=4)
    return details

