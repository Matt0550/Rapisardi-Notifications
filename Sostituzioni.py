###########################################################
# ITET Rapisardi da Vinci - Sostituzioni API (Unofficial) #
###########################################################

# Created by: @Matt0550 (GitHub)

import requests
from bs4 import BeautifulSoup

class Sostituzioni:
    def __init__(self, url):
        self.url = url
        
    def getTodayUpdates(self):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        url = self.url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Get the table inside the div with id LayoutDiv2
        table = soup.find("div", {"id": "LayoutDiv2"}).find("table")
        # From first tr get the text of first td
        date = table.find("tr").find("td").text
        # Get only the end 11 characters
        date = date[-11:-1]
        
        # From second tr insert into a list all the td starting from the second
        ore = [td.text for td in table.find_all("tr")[1].find_all("td")[1:]]
        # Insert into a list all the tr starting from the third
        rows = table.find_all("tr")[2:-1]
        
        result = []
        for row in rows:
            # Get the first td and the text inside
            classe = row.find("td").text
            # Get all the td starting from the second
            sostituzioni = [td.text for td in row.find_all("td")[1:]]
            # Get the docenti assenti, is the last tr
            docentiAssenti = table.find_all("tr")[-1].find_all("td")[1:]
            # Strip, replace \n and transform to string
            docentiAssenti = [td.text.strip().replace("\n", "") for td in docentiAssenti]
            docentiAssenti = "".join(docentiAssenti)

            # Create a dictionary with the data
            data = {
                "date": date,
                "ore": ore,
                "classe": classe,
                "sostituzioni": sostituzioni,
                "docentiAssenti": docentiAssenti
            }
            result.append(data)
        return result

    def getNextUpdates(self):
        # url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
        url = self.url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Get the table inside the div with id LayoutDiv2
        table = soup.find("div", {"id": "LayoutDiv3"}).find("table")
        # From first tr get the text of first td
        date = table.find("tr").find("td").text
        # Get only the end 11 characters
        date = date[-11:-1]

        # From second tr insert into a list all the td starting from the second
        ore = [td.text for td in table.find_all("tr")[1].find_all("td")[1:]]
        # Insert into a list all the tr starting from the third
        rows = table.find_all("tr")[2:-1]
        
        result = []
        for row in rows:
            # Get the first td and the text inside
            classe = row.find("td").text
            # Get all the td starting from the second
            sostituzioni = [td.text for td in row.find_all("td")[1:]]
            # Get the docenti assenti, is the last tr
            docentiAssenti = table.find_all("tr")[-1].find_all("td")[1:]
            # Strip, replace \n and transform to string
            docentiAssenti = [td.text.strip().replace("\n", "") for td in docentiAssenti]
            docentiAssenti = "".join(docentiAssenti)       


            # Create a dictionary with the data
            data = {
                "date": date,
                "ore": ore,
                "classe": classe,
                "sostituzioni": sostituzioni,
                "docentiAssenti": docentiAssenti
            }
            result.append(data)
        return result
    
    def getAllUpdates(self):
        return {"today": self.getTodayUpdates(), "next": self.getNextUpdates()}

    def getTodayUpdatesFromClass(self, classe):
        updates = self.getTodayUpdates()
        for update in updates:
            if update["classe"].lower() == classe.lower():
                return update
        return None
    
    def getNextUpdatesFromClass(self, classe):
        updates = self.getNextUpdates()
        for update in updates:
            if update["classe"].lower() == classe.lower():
                return update
        return None    