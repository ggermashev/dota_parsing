import re

import requests
from bs4 import BeautifulSoup
import psycopg2

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

parse_skins()
