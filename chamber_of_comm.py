import requests
from bs4 import BeautifulSoup
import numpy as np
import pymysql
import time
from random import randint
from time import sleep
import re

# defining user-agents
headers = {"User-Agent": "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}

# Database connection
conn = pymysql.connect(host='127.0.0.1', user='root', passwd=None, db='mysql',
                       charset='utf8')
cur = conn.cursor()
cur.execute("USE houzz")


# storing data
def store(Name, Details, Email, Number, Profile_url, Website, Address, Catagory, City, State, Country, Facebook,
          Twitter,
          Last_count):
    cur.execute(
        'INSERT IGNORE INTO lead_master_twmp (Name, Details, Email, Number, Profile_url, Website, Address, Catagory, City, State, Country, Facebook, Twitter, Last_count) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (Name, Details, Email, Number, Profile_url, Website, Address, Catagory, City, State, Country, Facebook, Twitter,
         Last_count))
    cur.connection.commit()


# counter
n = 0

# make array
pages = np.arange(n, 9115, 1)

for p in pages:
    a = p
    try:
        # make request to target website
        page = requests.get(
            "https://www.chamberofcommerce.com/retail-stores/clothing-and-accessories/?pg=" + str(
                p),
            headers=headers)
        print(page)
    # if connection error occurs then,
    except requests.exceptions.ConnectionError:
        print("Connection refused by the server..")
        print("Let me sleep for 5 seconds")
        print("ZZzzzz...")
        time.sleep(15)
        print("Was a nice sleep, now let me continue...")
        continue

    soup = BeautifulSoup(page.text, 'html.parser')

    # retrieve all containers of profiles
    containers = soup.find_all('div', class_="list_businesses")

    # sleep for better scraping
    sleep(randint(2, 10))

    # loop through each container
    for container in containers:
        try:
            sites1 = container.find('div', class_="bussiness_name")
        except:
            continue

        try:
            sites2 = sites1.find('a').get('href')  # slave link
        except:
            continue

        # defining master link
        site = "https://www.chamberofcommerce.com"

        # slave link and master link will make original profile url
        profile_url = site + sites2
        print(profile_url)

        # splitting slave link to get city, state, country

        location = sites2.split('/')

        try:
            country = location[1]
        except:
            country = 'NULL'

        try:
            state = location[2]
        except:
            state = 'NULL'

        try:
            city = location[3]
        except:
            city = 'NULL'

        print(city, state, country)

        try:  # making request to profile url
            url = requests.get(profile_url)
            print(url)

        # if connection error occurs then,
        except requests.exceptions.ConnectionError:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(15)
            print("Was a nice sleep, now let me continue...")
            continue
        details = BeautifulSoup(url.text, 'html.parser')

        # retrieving name of the destination profile

        try:
            name = details.find('div', class_="profile_business_name").text
        except:
            name = 'NULL'
        print(name)

        # retrieving address

        try:
            raw_add = details.find_all('div', class_='detail_text')
            address = raw_add[0].text.strip()
        except:
            address = 'NULL'
        print(address)

        # retrieving contact number

        try:
            number = details.find('span', class_="d-none d-sm-block phone-align").text.strip()
        except:
            number = 'NULL'
        print(number)

        # retrieving main information or description

        try:
            info = details.find('div', class_='about_p_text').text
        except:
            info = 'NULL'
        print(info)

        # retrieving contact info

        try:
            contact_info = details.find('ul', class_='info_list')
            contact_list = contact_info.find_all('li')

            # retrieving website

            try:
                website = contact_info.select_one('.info_list .spr-web-icon+ a')
                website = website.get('href')
            except:
                website = 'NULL'
            print(website)

            # retrieving email-id

            try:
                email = contact_info.find_all("a", href=re.compile(r"^mailto:"))
                email = email[0].text
            except:
                email = 'NULL'
            print(email)

            # retrieving facebook profile link

            try:
                facebook = contact_info.select_one('.spr-fb-icon+ a')
                facebook = facebook.get('href')
            except:
                facebook = 'NULL'
            print(facebook)

            # retrieving twitter profile link

            try:
                twitter = contact_info.select_one('img+ a')
                twitter = twitter.get('href')
            except:
                twitter = 'NULL'
            print(twitter)

        except:
            facebook = 'NULL'
            twitter = 'NULL'
            website = 'NULL'
            email = 'NULL'

        # storing last page no. which is just scraped

        n = n + 1
        last_count = int(a)
        category = 'clothes'

        store(name, info, email, number, profile_url, website, address, category, city, state, country, facebook,
              twitter, last_count)
