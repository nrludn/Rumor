import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from PyPDF2 import PdfReader



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

def read_daily_pdfs():
    folder_path = '/Users/dursun/Desktop/PythonProject/document_output'
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
                entry = {'disc_index' : disc_index, 'company_name': company_name, 'text': text}
                output_list.append(entry)
    return output_list


