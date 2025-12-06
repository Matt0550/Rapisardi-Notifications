###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)

import requests
from bs4 import BeautifulSoup

class Orario:
    def __init__(self, url):
        self.url = url
        # Add trailing slash if not present
        if not self.url.endswith("/"):
            self.url += "/"
        
    def getAllClassesTimetable(self, onlyNames=False):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # From first td get a elements and return [{orarioImage: "href.replace("html", "jpg")", name: ""}]

        # The table has 2 rows. The first row has headers (CLASSI, DOCENTI, AULE).
        # The second row has the content.
        # td indices: 0, 1, 2 are headers. 3, 4, 5 are content.
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
        page = requests.get(self.url)
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
        page = requests.get(self.url)
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

    def getSostegnoTimetable(self):
        page = requests.get(self.url + "orario_docenti_sostegno.php")
        soup = BeautifulSoup(page.content, 'html.parser')
        
        docenti_sections = soup.find_all("div", class_="docente-section")
        result = []
        
        for section in docenti_sections:
            name_div = section.find("div", class_="docente-nome")
            if not name_div:
                continue
            
            name = name_div.text.strip()
            
            table = section.find("table", class_="orario-table")
            if not table:
                continue
                
            # Parse headers
            headers = [th.text.strip() for th in table.find_all("th")]
            # headers[0] is "Ora", others are days
            days = headers[1:]
            
            timetable = {}
            rows = table.find("tbody").find_all("tr")
            
            for row in rows:
                cols = row.find_all("td")
                if not cols:
                    continue
                    
                ora = cols[0].text.strip()
                # Iterate over days
                for i, day in enumerate(days):
                    if i + 1 < len(cols):
                        value = cols[i+1].text.strip()
                        if day not in timetable:
                            timetable[day] = {}
                        timetable[day][ora] = value
            
            result.append({
                "name": name,
                "timetable": timetable
            })
            
        return result

