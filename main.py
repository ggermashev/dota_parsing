import random
import re
import time
import numpy as np
import requests
from bs4 import BeautifulSoup
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager




def parse_heroes():
    rq = requests.get("https://dota2.ru/heroes/").text
    soup = BeautifulSoup(rq, features='html.parser')
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    for s in soup.find_all('a', class_='base-hero__link-hero'):
        hero = s.get('data-title')
        rq1 = requests.get("https://dota2.ru" + str(s.get('href'))).text
        soup1 = BeautifulSoup(rq1, features='html.parser')
        description = soup1.find('div', class_='base-hero-hero__descr-text').find('p')
        if (description): description = description.text
        else: description = soup1.find('div', class_='markup-2BOw-j messageContent-2qWWxC').text
        description = description.replace("'", '`')
        hero = hero.replace("'", '`')
        print(hero)
        print(description)
        cursor.execute(f"insert into heroes (name, description) values ('{hero}', '{description}');")
    conn.commit()
    cursor.execute("update heroes set description = replace(description,' ', '')")
    conn.commit()
    cursor.close()
    conn.close()

def parse_heroes_spells():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    rq = requests.get("https://dota2.ru/heroes/").text
    soup = BeautifulSoup(rq, features='html.parser')
    for s in soup.find_all('a', class_='base-hero__link-hero'):
        hero = s.get('data-title').lower().replace("'", '`')
        rq1 = requests.get("https://dota2.ru" + str(s.get('href'))).text
        soup1 = BeautifulSoup(rq1, features='html.parser')
        for s1 in soup1.find_all('div', class_='base-hero-hero__skill global-content') :
            spell_name = s1.find('div', class_='base-hero-hero__skill-title').text.strip().replace("'", '`')
            manacost_and_cd = s1.find('div', class_='base-hero-hero__skill-manacost')
            manacost = ''
            cd = ''
            if (manacost_and_cd is not None):
                if (re.findall(r".*Расход маны.*\d+/*\d*/*\d*/*\d*", manacost_and_cd.text)):
                    manacost = re.search(r"\d+/*\d*/*\d*/*\d*", re.search(r".*Расход маны.*(\d+/*\d*/*\d*/*\d*)", manacost_and_cd.text)[0])[0]
                if (re.findall(r".*Перезарядка.*\d+/*\d*/*\d*/*\d*", manacost_and_cd.text)):
                    cd = re.search(r"\d+/*\d*/*\d*/*\d*", re.search(r".*Перезарядка.*(\d+/*\d*/*\d*/*\d*)", manacost_and_cd.text)[0])[0]
            description = s1.find('div', class_='base-hero-hero__skill-img').find('div').text.strip().replace("'", '`')
            cursor.execute(f"select id from heroes where name = '{hero}';")
            hero_id = cursor.fetchone()[0]
            # print(hero)
            # print(spell_name)
            # print(manacost)
            # print(cd)
            # print(description)
            # print(hero_id)
            cursor.execute(f"insert into spells (name, cd, manacost, description, hero_id) values ('{spell_name}', '{cd}', '{manacost}', '{description}', '{hero_id}')")
    conn.commit()
    cursor.close()
    conn.close()

    # f = open('spells.txt', 'a')
    # for h in heroes:
    #     f.write(h + ': ')
    #     for s in spells[h]:
    #         f.write(s + ",")
    #     f.write("\n")
    # f.close()

def parse_skins() :
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    #f = open('skins.txt', 'w')
    rq = requests.get('https://dota2.fandom.com/wiki/Equipment').text
    soup = BeautifulSoup(rq, features='html.parser')
    for s in soup.find_all('div',class_='heroentry'):
        href = s.find('a').get('href')
        hero = s.find('div', class_='heroentrytext').text.lower().replace("'",'`')
        rq_hero = requests.get("https://dota2.fandom.com" + str(href)).text
        soup_hero = BeautifulSoup(rq_hero, features='html.parser')
        for s_hero in soup_hero.find_all('tr'):
            if s_hero.find('td', class_='notanavbox-group'):
                slot = s_hero.find('td', class_='notanavbox-group').text.replace("'",'`')
                if (slot != 'Sets' and slot != 'Mount' and slot != 'Taunt'):
                    cursor.execute(f"select * from slots where name='{slot}'")
                    if (cursor.fetchone() is None):
                        cursor.execute(f"insert into slots (name) values ('{slot}')")
                    for skins in s_hero.find_all('div', class_='cosmetic-label'):
                        name = skins.find('a').get('title').replace("'",'`')
                        cursor.execute(f"select id from slots where name='{slot}'")
                        slot_id = cursor.fetchone()[0]
                        cursor.execute(f"select id from heroes where name='{hero}'")
                        hero_id = cursor.fetchone()[0]
                        cursor.execute(f"insert into skins (name, hero_id, slot_id) values ('{name}', '{hero_id}', '{slot_id}')")
    conn.commit()
    cursor.close()
    conn.close()
    # f.write(str(all_skins))
    # f.close()

all_hrefs = []
all_names = []
all_descriptions = []
def parse_guilds():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()

    link = "https://stratz.com/guilds/leaderboard?region=3&orderBy=PREVIOUS_WEEK_RANK&order=ASC"
    driver = webdriver.Chrome(ChromeDriverManager().install())

    driver.get(link)
    driver.implicitly_wait(5)
    all_names = []
    driver.implicitly_wait(5)
    window_before = driver.current_window_handle
    for i in range(170):
        driver.implicitly_wait(5)
        h = driver.find_element(By.XPATH, "//div[@class='sc-gsDKAQ lmKrvy']").find_elements(By.TAG_NAME, "a")[i]
        driver.implicitly_wait(5)
        driver.execute_script("arguments[0].scrollIntoView();", h)
        driver.execute_script("window.scrollBy(0,-50)", "")
        driver.implicitly_wait(10)
        all_names.append(driver.find_elements(By.XPATH,
                                             "//div/span[@class='sc-dkPtRN dEvUDf']")[i].text.replace("'", "`"))
        h.click()
        driver.implicitly_wait(10)
        all_descriptions.append(driver.find_element(By.XPATH, "//div[@class='sc-gsDKAQ cQJMWK']").find_element(By.XPATH,"//span[@class='sc-cTAIfT eJOwMO']").text)
        driver.back()
        driver.switch_to.window(window_before)
    for i in range(min(len(all_names),len(all_descriptions))):
        name = all_names[i].replace("'", "`")
        descr = all_descriptions[i].replace("'","`")
        cursor.execute(f"insert into guilds (name,description) values ('{name}', '{descr}')")
    conn.commit()
    cursor.close()
    conn.close()


def parse_players():
    link = 'https://www.dotabuff.com/players/leaderboard?page=1'
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(link)
    names = []
    money = []
    mmr = []
    for k in range(80):
        driver.implicitly_wait(5)
        found_names = driver.find_elements(By.XPATH, "//td/a[@class=' link-type-player']")
        for n in found_names:
            names.append(n.text.replace("'", "`").replace('"', "`"))
            money.append(np.random.randint(1000, 10000))
            mmr.append(np.random.randint(500, 7000))
        driver.implicitly_wait(5)
        btn = driver.find_element(By.XPATH, "//span/a[@rel='next']")
        btn.click()
    for i in range(len(names)):
        cursor.execute(f"Insert into players (name, money, mmr) values ('{names[i]}', '{money[i]}', '{mmr[i]}')")
    conn.commit()
    cursor.close()
    conn.close()

def generate_matches():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    for i in range(1000000):
        duration = np.random.randint(25,51)
        date_year = str(np.random.randint(2010,2023))
        date_month = str(np.random.randint(1,13))
        date_day = str(np.random.randint(1,28))
        date = date_year + "/" + date_month + "/" + date_day
        win_side = np.random.randint(0,2)
        if win_side == 0:
            win_side = "radiant"
        else:
            win_side = "dire"
        gamemode_id = np.random.randint(1,7)
        cursor.execute(f"insert into matches (duration, date, win_side, gamemode_id) values "
                       f"('{duration}', to_date('{date}','YYYY/MM/DD'), '{win_side}', '{gamemode_id}')")
    conn.commit()
    cursor.close()
    conn.close()

def generate_playes_matches():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from matches")
    games_total = int(cursor.fetchone()[0])
    for i in range(5, games_total+1):
        team = []
        heroes = []
        for j in range(10):
            player_id = np.random.randint(84,2334)
            match_id = i
            hero_id = np.random.randint(1,124)
            while player_id in team:
                player_id = np.random.randint(84, 2334)
            team.append(player_id)
            while hero_id in heroes:
                hero_id = np.random.randint(1, 124)
            heroes.append(hero_id)
        for j in range(5):
            cursor.execute(f"insert into players_matches (side, player_id, match_id, hero_id) values "
                           f"('radiant', '{team[j]}', '{i}', '{heroes[j]}')")
        for j in range(5,10):
            cursor.execute(f"insert into players_matches (side, player_id, match_id, hero_id) values "
                           f"('dire', '{team[j]}', '{i}', '{heroes[j]}')")
    conn.commit()
    cursor.close()
    conn.close()

def guilds_to_players():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='', host='localhost')
    cursor = conn.cursor()
    cursor.execute(f"select count(*) from players")
    players_amount = cursor.fetchone()[0]
    for i in range(players_amount):
        k = i + 84
        guild_id = np.random.randint(1, 171)
        chance = np.random.randint(1, 10)
        if chance > 2:
            cursor.execute(f"update players set guild_id = '{guild_id}' where id = {k}")
    conn.commit()
    cursor.close()
    conn.close()

def add_skin_cost():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    cost = np.random.normal(1000, 200, 8535)
    i = 1
    for c in cost:
        cur.execute(f"update skins set cost={c} where id={i}")
        i += 1
    conn.commit()
    cur.close()
    conn.close()

def add_possessions():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    players = [[] for i in range(0, 84 + 2251)]
    for i in range(500000):
        player_id = 83 + np.random.randint(1, 2251)
        skin_amount = int(np.random.normal(5, 3, 1))
        while skin_amount <= 0:
            skin_amount = int(np.random.normal(5, 3, 1))
        is_active = 'False'
        skin_id = np.random.randint(1, 8535)
        if (skin_id in players[player_id]):
            continue
        players[player_id].append(skin_id)
        cur.execute(f"insert into possesions (player_id, skin_amount, skin_id) values ('{player_id}', '{skin_amount}', '{skin_id}')")
    conn.commit()
    cur.close()
    conn.close()

def add_is_active():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    cur.execute(f"select skin_id from possesions")
    skin_ids = cur.fetchall()
    for s_id in skin_ids:
        cur.execute(f"select slot_id from skins where id={s_id[0]}")
        slot_id = cur.fetchone()[0]
        cur.execute(f"select skin_id, player_id from possesions where {slot_id}=(select slot_id from skins where skins.id=skin_id) and is_active=True")
        active = cur.fetchall()
        if len(active) == 0:
            cur.execute(f"update possesions set is_active=True where skin_id={s_id[0]}")
            conn.commit()
    cur.close()
    conn.close()

def guild_players_amount():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    cur.execute(f"select guild_id from players")
    guilds = cur.fetchall()
    set_guilds = set(guilds)
    for s_g in set_guilds:
        if s_g[0] is None:
            continue
        count = guilds.count(s_g)
        cur.execute(f"update guilds set players_amount={count} where id={s_g[0]}")
    conn.commit()
    cur.close()
    conn.close()

def date_to_tamstamp():
    conn = psycopg2.connect(dbname='Dota', user='postgres', password='postgres', host='localhost')
    cur = conn.cursor()
    for i in range(1,1110011):
        date_year = str(np.random.randint(2010, 2023))
        date_month = str(np.random.randint(1, 13)).rjust(2, '0')
        date_day = str(np.random.randint(1, 28))
        date_hours = str(np.random.randint(0, 24))
        date_minutes = str(np.random.randint(0, 60))
        time = f"{date_day} {date_month} {date_year} {date_hours}:{date_minutes}"
        cur.execute(f"update matches set time=to_timestamp('{time}', 'DD MM YYYY HH24:MI') where id={i}")
    conn.commit()
    cur.close()
    conn.close()
