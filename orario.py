###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)

import requests
from bs4 import BeautifulSoup

class Orario:
    def __init__(self, url):
        self.url = url
        
    def getAllClassesTimetable(self, onlyNames=False):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        url = self.url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # From first td get a elements and return [{orarioImage: "href.replace("html", "jpg")", name: ""}]

        classes = soup.find_all("td")[3]
        classes = classes.find_all("a")

        result = []
        for classe in classes:
            if onlyNames:
                result.append(classe.text)
            else:
                result.append({
                    "orarioImage": self.url + classe["href"].replace("html", "jpg"),
                    "name": classe.text
                })
        return result


    def getAllDocentiTimetable(self, onlyNames=False):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        url = self.url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # From first td get a elements and return [{orarioImage: "href.replace("html", "jpg")", name: ""}]

        classes = soup.find_all("td")[4]
        classes = classes.find_all("a")

        result = []
        for classe in classes:
            if onlyNames:
                result.append(classe.text)
            else:
                result.append({
                    "orarioImage": self.url + classe["href"].replace("html", "jpg"),
                    "name": classe.text
                })
        return result

    def getAllAuleTimetable(self, onlyNames=False):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        url = self.url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # From first td get a elements and return [{orarioImage: "href.replace("html", "jpg")", name: ""}]

        classes = soup.find_all("td")[5]
        classes = classes.find_all("a")

        result = []
        for classe in classes:
            if onlyNames:
                result.append(classe.text)
            else:
                result.append({
                    "orarioImage": self.url + classe["href"].replace("html", "jpg"),
                    "name": classe.text
                })
        return result

