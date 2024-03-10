import requests
import pandas as pd
import json
from bs4 import BeautifulSoup
import time

def get_bist100():
    url = "https://www.kap.org.tr/tr/Endeksler"
    r = requests.get(url)
    s=BeautifulSoup(r.text,"html.parser")
    s1=s.find('div', class_='column-type7 wmargin')
    s2=s.find_all('div', class_='comp-cell _02 vtable')

    hisse_kod=[]
    for i in s2:
        hisse_kod.append(i.text.strip('\n'))
        if len(hisse_kod) >99:
            break

    file_path = 'bist100.json'
    with open ('bist100.json','w', encoding='utf8') as f:
        json.dump(hisse_kod, f, ensure_ascii=False, indent=4)

    return hisse_kod

def get_company_id(surl):
    time.sleep(1)
    g = requests.get(url=surl)
    soup = BeautifulSoup(g.text, 'html5lib')
    cid = soup.select('img.comp-logo')[0]['src'].split('/')[-1]
    return cid

def get_bist_companies(output='pd'):
    """
    output format : 'pd' as dataframe or 'json' or 'dict
    """
    r = requests.get("https://www.kap.org.tr/tr/bist-sirketler")
    s = BeautifulSoup(r.text, 'html5lib')
    all_firms = s.find_all(class_='w-clearfix w-inline-block comp-row')

    companies_dict = {'companies': []}
    bist_100_c = get_bist100()


    for firm in all_firms:
        temp_dict = {'company_id': None}

        company = firm.select('div.comp-cell._04.vtable a.vcell')[0].text
        temp_dict['company'] = company
        temp_dict['company'] = temp_dict['company'].split(', ')[0]

        if temp_dict['company'] in ['KRDMA', 'SEK', 'ISATR', 'TSK', 'TVB', 'YKB']:
            temp_dict['company'] = {'KRDMA': 'KRDMD', 'SEK': 'SKBNK', 'ISATR': 'ISCTR', 'TSK': 'TSKB', 'TVB': 'VAKBN', 'YKB': 'YKBNK'}[temp_dict['company']]

        temp_dict['name'] = firm.select('div.comp-cell._14.vtable a.vcell')[0].text

        link = firm.select("div.comp-cell._04.vtable a.vcell")[0]
        temp_dict['link'] = 'https://www.kap.org.tr' + link['href']

        temp_dict['city'] = firm.select('div.comp-cell._12.vtable div.vcell')[0].text

        temp_dict['company_id'] = get_company_id(temp_dict['link'])
        if temp_dict['company'] in bist_100_c :
            temp_dict['company_index'] ="BIST100"
        else :
            temp_dict['company_index'] = None


        companies_dict['companies'].append(temp_dict)


    comp_json = json.dumps(companies_dict['companies'], indent=4, ensure_ascii=False)

    with open('bist_companies_info.json', 'w', encoding='utf8') as f:
        f.write(comp_json)

    if output == 'pd':
        output = pd.DataFrame(companies_dict['companies'])
        return output
    elif output == 'dict':
        return companies_dict['companies']
    elif output == 'json':
        comp_json = json.dumps(companies_dict['companies'], indent=4, ensure_ascii=False)
        return comp_json

