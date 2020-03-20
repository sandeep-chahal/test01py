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
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": "corona-virus-710f0",
        "private_key_id": "68f391bb3b522209c7fdf0f2b300c187552bbb79",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCgX4otEWp5qgPS\nQsrgDydFvUSNjRtrNcaAJ5V87382PP3gT8ni3ISti+FmkWSrFVfZjm5bKioY4dgO\nlkPWbr4hYhI9w/WG4FaoHzTLDuxBe4UUpPdW5zhXatSoQT/zMqsKtb/+7oY8SNS3\nJIZ7XoOPOTp+4zSskDQG94iQB/oxmABlf+XETwoFtZQW8n7rTWXbfCWcWt4awvR5\nZg7FGkDhfV6/ftUU0ZfHJNSSSPI6HQoHaWu1234glo5nDut+ReyxeTuRv7QhkM3q\nH3IfTlUebquW0E+sgxVL/uhh2/oz6eTZB1A/61dSNl1hCmqbeucxgHA+K0SmcXG1\nQq9AN+GLAgMBAAECggEAAhtfOFpbOL/4DuIbwjfQv0TOSsHI027AbdyXRS3sUO0a\nNME3mMhm4dTNoEhWtzyvi8coQgBazzrgWMi2mXGZA91C+hbB+gSmfszyJ5zJk86o\nn+3O5hBhmBxqMM+ypGJNBvX+UL4Xe2FFkiZjsek69z28PACGJ6I5XMIRxDqmmdIt\nDNEZ3JkBkBzAr98Iy7U8jXz0joSO+B4luGgQrMiUge3XQadbJjjaUtQ5CIYmgGAd\ndVyHotXKaGp7CyotpHY04J0HApc0hzJ+7qYpKPZFDV9POMtxoLyScZ0SeFWcGIB/\n1qjW3CWzktQ5jEueUZbcKdlSm7nbemGLWu+SIIbIAQKBgQDg2rRIrp3EUMZ1Oss5\n6PS7XdM1bRhowFpzAQbW494Oio5Rgnxnk+u082FC44yGZ2e2uoc/dWtZNMeoD/tn\nMW5Mc74G9bb6/ePqH9DireaQgfETRRTyl7gmqGpde9iFZsPFx/Mxe/eNO1Z2zF3e\n/T0CeXcDqIMbRKjORFsQm23ViwKBgQC2llikm4eZOI6MY4VTD2tR+AIfndTlitaQ\nxEEp80veV2zEPuieZA51NSAUSP63yGpyrOyUgW0ZQ42l7N0puNFH/PEiSehHcK0m\nDS2dFWcrS86WzTkCC4QdQ6/fOA1wAsnZJbCobr/XA5uzSRpf2VtnCRAgdDe18pN+\nuhHSWZekAQKBgQCCD39Am2A+ccqZfIyYzprg1gCZYqU/0iN/ahSer+d92b9Afo2f\nC/zHChA0NJLQG3fuRi59Elopm1HxcG0m33zBVCGSvQY+YCU5A3Y76AL5i2/6iXb4\na7HlCn2b3Ur8vth2ypVtBhvG4Y+937Bcj3Z+u+uPfiV33FsYFInoLT92yQKBgHuP\nVsFeNu8rZNwAZTMGVjwMN3Op3W7Q+87P4MFA0fDO/N35LHYzg80xfFn949H/IHom\nJ5t/0pKsMmk815XqakXrGEt59GSUDbiYZmvNFhoonM9UZeXKYUdkjNnkFsPcPzhh\n1yDEgbJB0NYM/Hosnzwk1/L+cs0AMWwrAvB0jLgBAoGAEyAFyo2iEdE+fJEXwN5m\ndGZ1N3e/HR3nE+F7nXFAQb0zmCQtqV/3f4AF+UNt1ROZrlpVrphbpe0h1HcjcmPs\nS6mq5sWpvawLHXVo6Jpasks4Z6Z/YeYWvAGcsUwIwwmBxEiP+aV169rHMxy2rAPq\nEehMils7B9M12kbviThGfuQ=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-dw194@corona-virus-710f0.iam.gserviceaccount.com",
        "client_id": "105778031209654692436",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-dw194%40corona-virus-710f0.iam.gserviceaccount.com"
    }
    )
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
