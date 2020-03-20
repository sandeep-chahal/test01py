import requests
from bs4 import BeautifulSoup
import json
import firebase_admin
from firebase_admin import credentials, firestore

import kivy
from kivy.app import App
from kivy.uix.button import Button


def get_death_rate():
    death_rate = {}
    url = "https://www.worldometers.info/coronavirus/coronavirus-death-toll/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find("tbody")
    rows = table.find_all("tr")
    for row in rows:
        feilds = row.find_all("td")
        date = feilds[0].text.replace("\xa0", "").replace(" ", "")
        deaths = feilds[1].text.replace(",", "").replace(" ", "")
        death_rate[date] = deaths
    return death_rate


def get_overview():
    overview = {}
    url = "https://www.worldometers.info/coronavirus/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    main_counter = soup.find_all("div", {"id": "maincounter-wrap"})
    for counter in main_counter:
        header = counter.find("h1").text.replace(
            ":", "").replace(",", "").replace(" ", "")
        value = counter.find("span").text.replace(
            ":", "").replace(",", "").replace(" ", "")
        overview[header] = value
    active = soup.find("div", {"class": "number-table-main"}).text.replace(
        ":", "").replace(",", "").replace(" ", "")
    overview["active"] = active
    serious = soup.find_all("span", {"class": "number-table"})[1].text.replace(
        ":", "").replace(",", "").replace(" ", "")
    overview["serious"] = serious
    return overview


def get_countries_data():
    countries = {}
    url = "https://www.worldometers.info/coronavirus/"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find(id="main_table_countries_today")
    table_body = table.find("tbody")
    rows = table_body.find_all("tr")
    for row in rows:
        feilds = row.find_all("td")
        countries[feilds[0].text] = {
            "total_cases": feilds[1].text.replace(",", "").replace("+", "").replace(" ", ""),
            "new_cases": feilds[2].text.replace(",", "").replace("+", "").replace(" ", ""),
            "total_deaths": feilds[3].text.replace(",", "").replace("+", "").replace(" ", ""),
            "new_deaths": feilds[4].text.replace(",", "").replace("+", "").replace(" ", ""),
            "total_recovered": feilds[5].text.replace(",", "").replace("+", "").replace(" ", ""),
            "active_cases": feilds[6].text.replace(",", "").replace("+", "").replace(" ", ""),
            "serious": feilds[7].text.replace(",", "").replace("+", "").replace(" ", "")
        }
    return countries


def save_as_json(data):
    json_obj = json.dumps(data)
    file = open("all_coutries.json", "w")
    file.write(json_obj)


def db_test(data):
    cred = credentials.Certificate("./cred.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    db.collection("cororna-virus").document("data").set(data)


def init():
    data = {}
    all_countries = get_countries_data()
    overview = get_overview()
    death_rate = get_death_rate()
    data["all_countries"] = all_countries
    data["overview"] = overview
    data["death_rate"] = death_rate
    db_test(data)


# init()


class MainApp(App):
    def build(self):
        button = Button(text='Hello from Kivy',
                        size_hint=(.5, .5),
                        pos_hint={'center_x': .5, 'center_y': .5})
        button.bind(on_press=self.on_press_button)

        return button

    def on_press_button(self, instance):
        init()
        print('Done')


if __name__ == '__main__':
    app = MainApp()
    app.run()
