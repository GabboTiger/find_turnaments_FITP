from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from time import sleep
import googlemaps
import csv
from sys import argv
import sys
import json

#first sure button (XPath)
b_tornei = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[1]/div/div/div/button"
b_tornei_fitp = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[1]/div/div/div/div/ul/li[3]/a"
b_stato = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[2]/div/div/div/button"
b_inProgramma = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[2]/div/div/div/div/ul/li[5]/a"
b_regione = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[6]/div/div/div/button"
b_tipo = "//*[@id='div-init-table']/div[1]/div/div/div[3]/div[3]/div[9]/div/div/div/button"

with open("/Users/gabriel/Developer/python/bot_internet/find_turnaments_fitp/buttons_xpath.json", "r") as file:
    var_buttons = json.load(file)

with open("/Users/gabriel/Developer/python/bot_internet/find_turnaments_fitp/personal_info.json", "r") as file:
    info = json.load(file)

    CLASSIFICA = info['ranking']
    CASA = info['address']
    API_key = info['API_KEYS_gmaps']

def press_bottoni(bottoni:list, driver):
    '''
    to click each botton to filter the turnaments
    '''
    for bottone in bottoni:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, bottone)))
        button = driver.find_element(By.XPATH, bottone)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        try:
            button.click()
        except:
            driver.execute_script("arguments[0].click();", button)

    # continue to click the 'carica altri' buttun while -> `display: none`
    while True:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btn-loadMore")))
            bottone = driver.find_element(By.ID, "btn-loadMore")
            # check if the button has `display: none`
            if bottone.get_attribute("style") and "display: none" in bottone.get_attribute("style"):
                break  # exit from the cicle
            # click the button
            bottone.click()
            # wait a moment before cecking again (to avoid too much click)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "btn-loadMore")))
        except Exception as e:
            #print(f"button don't find error: {e}")
            break

def distanza(info_tornei:list, max_range=False):
    """
    max_range=True -> toglie i tornei a più di 1h
    """
    try:
        gmaps = googlemaps.Client(key=API_key)
        list_remove = []
        for torneo in info_tornei:
            try:
                distanza = gmaps.distance_matrix(CASA, torneo[3])['rows'][0]['elements'][0] #['rows'][0]['elements'][0] => give the distance using google maps api
            except:
                distanza = None
            try:
                if distanza == None:
                    torneo.append(distanza)
                elif max_range:
                    torneo.append(distanza['duration']['text'])
                else:
                    val_distanza = distanza['duration']['text'].split()
                    if len(val_distanza) <= 2:
                        torneo.append(distanza['duration']['text'])
                    else:
                        list_remove.append(torneo) # -> indice elementi da rimuevere
            except:
                torneo.append(None)
        for torneo in list_remove:
            info_tornei.remove(torneo)
    except:
        print('API not valid')

    return

def extrac_info(driver):
    '''
    extracting the informations from the page
    '''
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    tornei = soup.find_all('span', class_='cc-title cc-clamp-d-2 cc-clamp-t-2')
    date = soup.find_all('span', class_='cc-label')
    luoghi = soup.find_all('span', class_='cc-note cc-note-2')
    classifiche = soup.find_all('div', class_='cc-row-extra')

    tornei = [torneo.text.strip() for torneo in tornei] #torneo.text take only the text from the HTML
    date_tornei = [data.text.strip() for data in date] 
    date_tornei.pop(0)
    luoghi_tornei = [luogo.text.strip() for luogo in luoghi]
    classifica_tornei = [dato.text.strip() for dato in classifiche]

    #put the info inside a list
    info_tornei = []
    for x in range(len(tornei)):
        info_tornei.append([tornei[x], date_tornei[x], luoghi_tornei[x], classifica_tornei[x]])

    return info_tornei

def ranking_filter(info_tornei:list):
    '''
    to filter the turnament to the only ones you can subscrie for yours ranking
    '''
    try:
        tornei_possibili = []
        for torneo in info_tornei:   
            torneo[3] = torneo[3].replace('Categorie classifica ', '')
            categorie = torneo[3].split(' - ')
            for x in range(len(categorie)):
                if categorie[x] == '4.NC':
                    categorie[x] = 4.7
                else:
                    categorie[x] = float(categorie[x])
                
            if CLASSIFICA < categorie[0] or CLASSIFICA > categorie[1]:
                pass
            else:
                tornei_possibili.append(torneo)
        return tornei_possibili
    except ValueError:
        print("ranking not valid")

def city(info_tornei:list):
    try:
        for torneo in info_tornei:
            luogo = torneo[2].split(' - ')
            torneo.pop(2)
            torneo.insert(2, str(luogo[:-1]))
            torneo[2] = torneo[2].strip('['']') 
            torneo.insert(3, luogo[-1])
    except ValueError:
        print("testo non valido")
    return

def variabili():
    regione = None
    tipo = None

    #choosing the region
    print("choose the region (from this ones):")
    for i in var_buttons['regione']:
        print(f'-> {i}')
    regione = input("... (ENTER for all): ")
    if regione.lower() not in var_buttons['regione'] and regione !='':
        print('regione non valida')
        sys.exit()
    
    #choosing the type of competition
    print('choose the type:')
    for i in var_buttons['tipo']:
        print(f'-> {i}')
    tipo = input("... (ENTER for all): ")
    if tipo.lower() not in var_buttons['tipo'] and tipo !='':
        print('regione non valida')
        sys.exit()
    
    limit = input('do you want to limit the distance to max 1h [y/n]: ')
    if limit == '':
        limit = 'y'
    return regione, tipo, limit


def main():
    #defining some variables:
    limiter = True
    regione, tipo, limit = variabili()
    if limit == 'n':
        limiter = False
    
    bottoni = [b_tornei, b_tornei_fitp, b_stato, b_inProgramma]
    if regione != '':
        b_place = var_buttons['regione'][regione.lower()]
        bottoni.append(b_regione)
        bottoni.append(b_place)
    if tipo != '':
        b_type = var_buttons['tipo'][tipo.lower()]
        bottoni.append(b_tipo)
        bottoni.append(b_type)

    if (CASA == '' or API_key == '') and limit == 'y':
        print('\n!!! ERROR:if you want the distanze complete the ./personal_info.json !!! \n')
        limiter = False
    
    print('\n... wait a moment ...')
    url = "https://www.fitp.it/Tornei/Ricerca-tornei"

    # initialize the webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    sleep(5)

    # acept the cookies ad press the buttons to filter the turnaments
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='iubenda-cs-banner']/div/div/div/div[3]/div[2]/button[2]")))
        driver.find_element(By.XPATH, "//*[@id='iubenda-cs-banner']/div/div/div/div[3]/div[2]/button[2]").click()
    except:
        pass
    press_bottoni(bottoni, driver)
    sleep(5)

    # working on the extracted data
    info = extrac_info(driver)
    if CLASSIFICA != '':
        info = ranking_filter(info)
    city(info)
    if limiter:
        distanza(info)

    # using csv.writer method from CSV package the put the information inside the the file ./turnaments.csv
    with open('turnaments.csv', 'w') as f:   
        write = csv.writer(f)
        write.writerows(info)
    
    print('\n DONE :) -> see ./turnaments.csv')

    return

if __name__ == '__main__':
    main()