# Connect to mysql

import MySQLdb
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase

# Check os
if os.name == "nt": # Windows
    # Open database connection
    db = MySQLdb.connect("192.168.1.21","rapisardi", "TwEm-z6GY.VWbVaB", "rapisardi_notifications")
else: # Linux
    # Open database connection
    db = MySQLdb.connect("0.0.0.0","root", "", "rapisardi_notifications")

# prepare a cursor object using cursor() method
cursor = db.cursor()

ADMIN_SUMMARY = True

# Setup SMTP server
smtp_server = "smtp.yandex.com"
smtp_port = 465
smtp_user = "rapisardi.updates@matt05.ml"
smtp_pass = os.environ.get("SMTP_PASS")
# Check if the SMTP password is set
# if smtp_pass == None:
#     print("SMTP password not set")
#     exit()

def sendEmail(to, subject, body, html=False):
    # Edit the mittent

    msg = MIMEMultipart()
    msg["From"] = "Rapisardi Updates <" + smtp_user + ">"
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))
    text = msg.as_string()
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(smtp_user, smtp_pass)
    server.sendmail(smtp_user, to, text)
    server.quit()


def getUserClassroomId(userId):
    sql = "SELECT classroom_id FROM users WHERE id = " + str(userId)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        classroomId = results[0][0]
    except:
        print("Error: unable to fetch data")
        return None
    return classroomId

def getUserAndClassroomData(userId):
    classroomId = getUserClassroomId(userId)

def getTodayUpdates():
    url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
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
        # Create a dictionary with the data
        data = {
            "date": date,
            "ore": ore,
            "classe": classe,
            "sostituzioni": sostituzioni
        }
        result.append(data)
    return result

def getNextUpdates():
    url = "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
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
        # Create a dictionary with the data
        data = {
            "date": date,
            "ore": ore,
            "classe": classe,
            "sostituzioni": sostituzioni
        }
        result.append(data)
    return result


adminSummary = []
def checkUpdates():
    pass

def sendMail(userId, movieData):
    # Get the user email
    sql = "SELECT email FROM users WHERE id = " + userId
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        email = results[0][0]
    except:
        print("Error: unable to fetch data")
        return None
    # Send mail
    print("Sending mail to " + email + " for " + movieData["path"])
    # To episodes split the string by , and for each episode add a <br>
    movieData["episodes"] = movieData["episodes"].replace(", ", "<br>")

    if movieData["title"] == "" or movieData["title"] == None:
        movieData["title"] = "Nuovi episodi aggiunti"

    subject = movieData["title"] + " - Aggiornamento"
    
    body = "Ciao, <br> <br> nella serie <b>" + movieData["title"] + "</b> sono stati aggiunti i seguenti episodi: <br> <br>" + movieData["episodes"] + "<br> <br> Clicca <a href='"+movieData["link"] + "'>qui</a> per andare alla pagina della serie. <br> <br> Cordiali saluti, <br> Matt05, rapisardi Updates"
    sendEmail(email, subject, body, True)
    adminSummary.append("Sent " + movieData["title"] + " to " + email)
    
def sendAdminSummary():
    print("Sending admin summary")
    body = "Riepilogo aggiornamenti: <br> <br> " + "<br> <br>".join(adminSummary)
    sendEmail("pchpmatt05@gmail.com", "Riepilogo aggiornamenti", body, True)

def main():
    checkUpdates()
    sendAdminSummary()

if __name__ == "__main__":
    print(getTodayUpdates())