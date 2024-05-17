import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

# Pfad zum ChromeDriver (passen Sie diesen Pfad an Ihre Systemkonfiguration an)
chromedriver_path = '/Users/kamillalauter/Downloads/chromedriver_mac64 (1)/chromedriver'

# Konfigurieren des Chrome-Browsers für Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialisieren des ChromeDriver-Dienstes
webdriver_service = Service(chromedriver_path)
try:
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)
except Exception as e:
    print(f"Error initializing ChromeDriver: {e}")
    exit()

# Funktion zum Extrahieren von Daten aus BeautifulSoup-Objekt
def extract_data(soup, selector):
    data = []
    elements = soup.select(selector)
    for element in elements:
        value = element.text.strip()
        data.append(value)
    return data

# Funktion zum Extrahieren von Kontaktdetails und Adresse von der zweiten Seite
def extract_contact_and_address(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    contact_info = None
    address_info = None

    contact_section = soup.find('h3', class_='title title--jp-card title--left', text='Deine Kontaktperson')
    if contact_section:
        contact_info = contact_section.find_next('div').text.strip()
        print('Kontaktdaten gefunden:', contact_info)
    else:
        print('Keine Kontaktdaten gefunden.')

    address_section = soup.find('div', class_='address')
    if address_section:
        address_info = address_section.text.strip()
        print('Adresse gefunden:', address_info)
    else:
        print('Keine Adresse gefunden.')

    return contact_info, address_info

# Funktion zum Speichern der Daten in einer CSV-Datei
def save_to_csv(data, filename, header):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(header)  # Header der CSV-Datei
        writer.writerows(data)

# Liste zum Speichern der Jobdaten
job_data = []

# Schleife über Seiten 1 bis 100
for page_num in range(1, 101):
    # URL für jede Seite
    url = f"https://www.ausbildung.de/suche/?form_main_search[what]=&form_main_search[where]=Hannover&t_search_type=root&t_what=&t_where=&page={page_num}"
    browser.get(url)
    # Warten, bis die Seite vollständig geladen ist
    time.sleep(5)

    # Abrufen des HTML-Inhalts der Seite
    html_content = browser.page_source

    # Verwenden von BeautifulSoup, um die Jobtitel zu extrahieren
    soup = BeautifulSoup(html_content, 'html.parser')

    job_titles = extract_data(soup, 'h3.job-posting-cluster-cards__title')
    job_locations = extract_data(soup, 'span.job-posting-cluster-cards__fact-value')
    job_addresses = extract_data(soup, 'strong.job-posting-cluster-cards__company')

    # Für jede Stelle Kontaktdetails und Adresse extrahieren
    for i in range(len(job_titles)):
        job_title_element = soup.find_all('h3', class_='job-posting-cluster-cards__title')[i]
        job_url = job_title_element.find_parent('a')['href'] if job_title_element.find_parent('a') else None
        if job_url:
            full_job_url = f"https://www.ausbildung.de{job_url}"
            print(full_job_url)
            contact_details, address_details = extract_contact_and_address(full_job_url)
            job_data.append([job_titles[i], job_locations[i], job_addresses[i], contact_details, address_details,full_job_url])

# Speichern der Jobdaten in einer CSV-Datei
save_to_csv(job_data, 'job_data.csv', ['Job Title', 'Location', 'Address', 'Contact', 'Secondary Address','Link'])

print(f"{len(job_data)} job entries have been saved to job_data.csv")

# Browser schließen
browser.quit()
