import requests
from bs4 import BeautifulSoup
import json
import regex as re
import pandas as pd
import time
from numpy import nan
import os
from PyPDF2 import PdfReader
from datetime import datetime, timedelta

def get_statement():
    with open('new_announcement.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    with open('bist100.json', 'r', encoding='utf-8') as a:
        bist_liste = json.load(a)    

    todate = datetime.today().date()
    output_folder = "statement_output"  
    folder_path = os.path.join(output_folder, str(todate))
    os.makedirs(folder_path, exist_ok=True)    
        
    pages = []
    for i in data:
        if i['ticker'] in bist_liste:
            link = f"https://www.kap.org.tr/tr/Bildirim/{i['disc_index']}"
            pages.append(link)
        
    full_liste = []
    disc_index_list = []
    for page, announcement in zip(pages, data):
        metin = {'disc_index': announcement['disc_index']} 
        r = requests.get(page)
        s = BeautifulSoup(r.text, 'html5lib')

        name = s.find(class_='type-medium bi-dim-gray')
        if name:
            company_name = name.get_text(strip=True).replace('"', '')
            if company_name == 'ISMEN, IYM':
                company_name = 'ISMEN'
            metin['company_name'] = company_name
            
        info = s.find(class_='text-block-value')
        if info:
            text = info.get_text(strip=True)
            metin['text'] = text
        full_liste.append(metin)
        
    for entry in full_liste:
        if 'text' not in entry or not entry['text'] or pd.isna(entry['text']):
            disc_index_list.append(entry['disc_index'])

    if disc_index_list:
        get_pdf_file(disc_index_list)

        print('Files reading')
        time.sleep(5)
        output = read_daily_pdfs()
        full_liste.extend(output)
        #full_liste = [i for i in full_liste if 'text' in i and pd.notna(i['text'])]

    cleaned_output = [entry for entry in full_liste if 'text' in entry and entry['text']]

    if cleaned_output:
        json_file_name = f"statement_{todate}.json"
        output_path = os.path.join(folder_path, json_file_name)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_output, f, ensure_ascii=False, indent=4)
    #return cleaned_output
    return pd.DataFrame(cleaned_output)


def get_pdf_file(disc_index_list):
    with open('new_announcement.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    todate = datetime.today().date()
    output_folder = "document_output"  
    folder_path = os.path.join(output_folder, str(todate))
    os.makedirs(folder_path, exist_ok=True) 

    for disc_index in disc_index_list:
        for announcement in data:
            if announcement['disc_index'] == disc_index:
                page_url = f"https://www.kap.org.tr/tr/Bildirim/{announcement['disc_index']}"
                
                response = requests.get(page_url)
                soup = BeautifulSoup(response.content, 'html.parser')
                pdf_link = soup.find("a", {"class": "modal-button", "href": f"/tr/BildirimPdf/{announcement['disc_index']}"})

                if pdf_link:
                    pdf_url = "https://www.kap.org.tr" + pdf_link['href']
                    pdf_file_name = f"{announcement['ticker']}_{announcement['disc_index']}.pdf"
                    output_path = os.path.join(folder_path, pdf_file_name)
                    
                    with open(output_path, "wb") as f:
                        pdf_response = requests.get(pdf_url)
                        f.write(pdf_response.content)
                        print(f"PDF kaydedildi: {output_path}")
    time.sleep(2)

def read_daily_pdfs():
    folder_path = 'document_output'
    today_date = datetime.today().strftime('%Y-%m-%d')
    today_folder_path = os.path.join(folder_path, today_date)

    output_list = []
    for file_name in sorted(os.listdir(today_folder_path)):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(today_folder_path, file_name)
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                text = ''
                for page in reader.pages:
                    text += page.extract_text()
                company_name, disc_index_with_extension = file_name.split('_')
                disc_index = disc_index_with_extension.split('.')[0]
                disc_index = int(disc_index.replace("'", ""))
                entry = {'disc_index' : disc_index, 'company_name': company_name, 'text': text}
                output_list.append(entry)
    return output_list


