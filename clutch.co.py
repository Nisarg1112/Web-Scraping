import requests
from bs4 import BeautifulSoup
import numpy as np
import pymysql
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# adding extra options to our Chrome browser for ease of access
options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-gpu')

# Database connection
conn = pymysql.connect(host='127.0.0.1', user='root', passwd=None, db='mysql',
                       charset='utf8')
cur = conn.cursor()
cur.execute("USE houzz")


# storing data
def store(Name, Ratings, Details, Email, Number, Profile_url, web, Website, Address, Catagory, City, State, Country,
          Not_matched, Last_count):
    cur.execute(
        'INSERT IGNORE INTO lead_master_twmp (Name, Ratings, Details, Email, Number, Profile_url, Website, Site_url, Address, Catagory, City, State, Country, Not_matched, Last_count) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (Name, Ratings, Details, Email, Number, Profile_url, web, Website, Address, Catagory, City, State, Country,
         Not_matched, Last_count))
    cur.connection.commit()


# defining user-agent for scraping
headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

# variable n is for keeping an eye on the no. last page retrieved
n = 0

# variable result is for keeping an eye on total results scraped
result = 1

# defining main link
link = "https://clutch.co/"

# making numpy array
pages = np.arange(n, 250, 1)

# looping through each page
for page in pages:
    # making request to required link
    try:
        page = requests.get("https://clutch.co/seo-firms?page=" + str(page),
                            headers=headers)
        print(page)
        n = n + 1
    # if connection error occurs then sleep for 15 seconds and try again
    except requests.exceptions.ConnectionError:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(15)
        print("Was a nice sleep, now let me continue...")
        n = n
        continue

    soup = BeautifulSoup(page.text, 'html.parser')

    # retrieving all the containers
    containers = soup.find_all('li', class_='provider-row')

    no_of_container = 0

    # looping through all the containers

    for container in containers:
        no_of_container = no_of_container + 1
        result = result + 1

        # finding all the 'li' tag in order to get main profile link
        profile_container = container.find_all('li')

        try:
            # 3rd element of profile_container list contains 'href' tag
            profile_slave = profile_container[2].find('a').get('href')

            # using regular expression matching profile_slave string that if it contains 'profile' in it or not
            profile1 = re.findall(r"^/profile", profile_slave)

            # if profile1 dosen't return any value then,
            if profile1 == []:
                profile_slave = prof[1].find('a').get('href')
            else:
                profile_slave = prof[2].find('a').get('href')
            print(profile_slave)
        except:

            # if its not profile link then, it must be an advertisement link
            print("advertisement link")
            result = result - 1
            continue
        profile = link + profile_slave

        try:  # finally retrieving profile_url
            profile_url = profile
        except:
            profile_url = 'NULL'
        print(profile_url)

        # making request to that particular profile link

        try:
            box = requests.get(profile, headers=headers)
            time.sleep(2)
            print(box)

        except requests.exceptions.ConnectionError:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(15)
            print("Was a nice sleep, now let me continue...")
            continue

        content = BeautifulSoup(box.text, 'html.parser')

        try:  # retrieving name
            name = content.find('h1', class_="page-title").text
        except:
            name = 'NULL'
        print(name)

        try:  # retrieving ratings of particular profile
            ratings = content.find('span', class_="rating").text
        except:
            ratings = 'NULL'

        try:  # retrieving summary or information that has been provided by respective owner
            summary = content.find('div', class_="expanding-formatter-summary").text
        except:
            summary = 'NULL'

        try:  # retrieving email if summary contains any, through regular expression
            emails = re.findall("([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", summary)
            email = emails[0]
        except:
            email = 'NULL'

        try:  # retrieving contact number
            num = content.find('div', class_="item")
            number = num.find('a').get("href").split(":")[1]
        except:
            number = "NULL"

        try:  # retrieving original website link
            web = content.find('div', class_="item website-link-a")
            website1 = web.find('a').get("href")
            website = website1.split("?")[0]
        except:
            website = "NULL"
        print(website)

        # for extraction of accurate address, use selenium

        try:  # initiating web-browser
            browser = webdriver.Chrome(executable_path=r'C:\Users\Pujan\PycharmProjects\chromedriver.exe',
                                       options=options)

            # getting respective profile_link on our chrome browser
            add = browser.get(profile)
            time.sleep(5)
            print('profile retrived')

            # Explicit wait - so we can wait until our required element is visible
            element = WebDriverWait(browser, 20).until(
                EC.presence_of_element_located((By.XPATH, """//*[@id="summary"]/div/div/div[3]/div/a""")))
            element.click()
            print('element clicked')
            time.sleep(9)

            try:  # retrieving street
                street = browser.find_element_by_xpath(
                    """//*[@id="summary"]/div/div/div[3]/div/div[3]/ul[1]/li/div/div/div/div[1]""").text
            except:
                street = "NULL"
            print(street)

            try:  # retrieving locality
                locality = browser.find_element_by_xpath(
                    """//*[@id="summary"]/div/div/div[3]/div/div[3]/ul[1]/li/div/div/div/span[1]""").text
            except:
                locality = "NULL"
            print(locality)

            try:  # retrieving region
                region = browser.find_element_by_xpath(
                    """//*[@id="summary"]/div/div/div[3]/div/div[3]/ul[1]/li/div/div/div/span[2]""").text
            except:
                region = "NULL"

            try:  # retrieving country
                country = browser.find_element_by_xpath(
                    """// *[ @ id = "summary"] / div / div / div[3] / div / div[3] / ul[1] / li / div / div / div / div[2]""").text
            except:
                country = "NULL"

            not_matched = 'No'

            # closing the opened browser for ease of access
            browser.close()


        except:
            try:
                browser.close()
            except:
                pass
            street = 'NULL'
            locality = 'NULL'
            region = 'NULL'
            country = 'NULL'
            not_matched = 'Yes'

        category = 18
        print(no_of_container)
        print(result)
        print(n)

        last_count = n

        # storing scraped results to our SQL Database

        store(name, ratings, summary, email, number, profile_url, website, website, street, category, locality, region,
              country, not_matched, last_count)
