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
smtp_user = "rapisardi.updates@studyapp.ml"
smtp_pass = os.environ.get("SMTP_PASS", "xJs@Ln^Txyx3N$DFLS5A")
# Check if the SMTP password is set
if smtp_pass == None:
    print("SMTP password not set")
    exit()

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


def getUserDataFromDB(userId):
    sql = "SELECT * FROM users WHERE id = " + str(userId)
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        return results[0]
    except:
        print("Error: unable to fetch data")
        return None


def getUserAndClassroomData(userId):
    userApiKey = getUserDataFromDB(userId)[1]

    # Make a request to api.studyapp.ml/user/info/partial with header apiKey
    r = requests.get("https://api.studyapp.ml/user/info/partial", headers={"apiKey": userApiKey})

    # Get the data
    data = r.json()

    return data["message"]

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
    # Get today updates if the hour is between 8 and 14 
    if datetime.now().hour >= 8 and datetime.now().hour <= 14:
        updates = getTodayUpdates()
    else:
        updates = getNextUpdates()
    
    # Get all the users
    sql = "SELECT * FROM users"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        for user in results:
            # Get the user data
            userData = getUserAndClassroomData(user[0])
            # Get the user classname
            userClass = userData["classroom"]["name"]
            print("Checking " + user[2] + " for " + userClass)

            # Check if the user has the same class as the update
            for update in updates:
                # Make a table with the data
                table = "<table><tr><th>Ora</th><th>Sostituzione</th></tr>"
                for i in range(len(update["ore"])):
                    table += "<tr><td>" + update["ore"][i] + "</td><td>" + update["sostituzioni"][i] + "</td></tr>"
                table += "</table>"
                # Send the mail
                sendEmailToUser(user, userData["user"]["email"], table, update["sostituzioni"], update["date"])
                # Add the user to the admin summary
                adminSummary.append(user[2] + " - " + update["date"])

    except Exception as e:
        print("Error: unable to fetch data")
        print(e)
        return None
    
def sendEmailToUser(userDBData, email, table, array, date):
    print(array)
    lastSent = userDBData[4]
    lastContent = userDBData[5]

    # Check if the email has already been sent but if the content is different send it again
    if lastSent != None and lastContent != None:
        if lastSent.strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d") and lastContent == str(array):
            print("Email already sent")
            return None
        else:
            # Send the email
            message = "Ciao, le sostituzioni in data " + date + " sono state aggiornate: <br> <br>" + table + "<br> <br> Buona giornata!"
            sendEmail(email, "Aggiornamento sostituzioni", message, True)

            # Update the last sent date and content
            sql = 'UPDATE users SET last_notification = "' + str(datetime.now()) + '", last_sostituzioni = "' + str(array) + '" WHERE id = ' + str(userDBData[0]) + ';'
            try:
                cursor.execute(sql)
                db.commit()
                print("Updated user " + userDBData[2])
                return True
            except Exception as e:
                print("Error: unable to update user")
                print(e)
                return None
    else:
        # Send the email
        message = "Ciao, le sostituzioni in data " + date + " sono state aggiornate: <br> <br>" + table + "<br> <br> Buona giornata!"
        sendEmail(email, "Aggiornamento sostituzioni", message, True)

        # Update the last sent date and content
        sql = 'UPDATE users SET last_notification = "' + str(datetime.now()) + '", last_sostituzioni = "' + str(array) + '" WHERE id = ' + str(userDBData[0]) + ';'
        try:
            cursor.execute(sql)
            db.commit()
            print("Updated user " + userDBData[2])
            return True
        except Exception as e:
            print("Error: unable to update user")
            print(e)
            return None



def sendAdminSummary():
    print("Sending admin summary")
    body = "Riepilogo aggiornamenti: <br> <br> " + "<br> <br>".join(adminSummary)
    sendEmail("pchpmatt05@gmail.com", "Riepilogo aggiornamenti", body, True)

def main():
    checkUpdates()
    sendAdminSummary()

if __name__ == "__main__":
    checkUpdates()