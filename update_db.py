"""
This script is used to send email with the updates of the substitutions to the users that have subscribed to the service
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from dotenv import load_dotenv
from sostituzioni import Sostituzioni
from pymongo import MongoClient

load_dotenv()

MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = int(os.getenv("MONGODB_PORT", 27017))
MONGODB_USERNAME = os.getenv("MONGODB_USERNAME")
MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE")

if MONGODB_USERNAME == None or MONGODB_USERNAME == "" or MONGODB_PASSWORD == None or MONGODB_PASSWORD == "":
    print("MongoDB username or password not set")
    exit()

# Connect to the database
client = MongoClient("mongodb+srv://" + MONGODB_USERNAME+ ":" + MONGODB_PASSWORD +"@" + MONGODB_HOST)
db = client[MONGODB_DATABASE]
usersDb = db.users

# Setup SMTP server
SMTP_SERVER = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_SSL = os.getenv("SMTP_SSL", True)
SMTP_FROM = os.getenv("SMTP_FROM")

# Check if the SMTP password is set
if SMTP_PASSWORD == None or SMTP_PASSWORD == "":
    print("SMTP password not set")
    exit()

def sendEmail(to, subject, body, html=False):
    # Edit the mittent

    msg = MIMEMultipart()
    msg["From"] = "Rapisardi Notifications <" + SMTP_FROM + ">"
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))
    text = msg.as_string()
    if SMTP_SSL == True or SMTP_SSL == "True":
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_FROM, to, text)
    server.quit()

def getUserDataFromDB(userId):
    # Get the user data from the database
    userData = usersDb.find_one({"id": userId})
    return userData

def fromSedeToURL(sede):
    if sede == "margherita":
        return "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"
    elif sede == "turati":
        return "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni2.php"
    elif sede == "serale":
        return "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni3.php"
    else:
        return "https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php"

def adaptDbUser(user):
    # Last sostituzioni
    # {
    #    "class": $array
    # }
    
    # Last notification
    # {
    #    "class": $now
    # }
        # Fix the last_sostituzioni and last_notification. Copy the classes to last_notification and the sostituzioni if not present. Then push the new data to the database

    if "last_sostituzioni" not in user:
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_sostituzioni": {}}})
    if "last_notification" not in user:
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_notification": {}}})
    if "classi" not in user:
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"classi": []}})
    if "endpoint" not in user:
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"endpoint": "margherita"}})

    if "last_sostituzioni" in user and "last_notification" in user:
        # Update the list adding missing class and remove the ones that are not in the classi array. If the class there is in the array don't touch
        for classe in user["classi"]:
            if classe not in user["last_sostituzioni"]:
                user["last_sostituzioni"][classe] = ""
            if classe not in user["last_notification"]:
                user["last_notification"][classe] = datetime.now()
        for classe in user["last_sostituzioni"]:
            if classe not in user["classi"]:
                del user["last_sostituzioni"][classe]
            if classe not in user["last_notification"]:
                del user["last_notification"][classe]
        # Update the last notification date
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_notification": user["last_notification"]}})
        # Update the last sostituzioni
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_sostituzioni": user["last_sostituzioni"]}})
    else:
        # Add the classes to the last sostituzioni and last notification
        lastSostituzioni = {}
        lastNotification = {}
        for classe in user["classi"]:
            lastSostituzioni[classe] = ""
            lastNotification[classe] = datetime.now()
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_notification": lastNotification}})
        usersDb.update_one({"_id": user["_id"]}, {"$set": {"last_sostituzioni": lastSostituzioni}})


def check(update, sede):
    print("Checking update for " + update["classe"])
    # Search users where the class is the same as the update 
    usersInClass = usersDb.find({"classi": update["classe"], "endpoint": sede})
    for user in usersInClass:

        # if len(list(usersInClass)) == 0:
        #     print("No users found for " + update["classe"] + " in the database")
        #     continue

        print("Checking " + update["classe"] + " for " + user["email"])
        adaptDbUser(user)


        # if update["classe"].lower() in user["classi"]:
        #     print("User " + user["email"] + " not subscribed to " + update["classe"])
        #     continue

        print("Found update for " + user["email"])
        # Make a table with the data
        table = "<table><tr><th>Ora</th><th>Sostituzione</th></tr>"
        for i in range(len(update["ore"])):
            table += "<tr><td>" + update["ore"][i] + "</td><td>" + update["sostituzioni"][i] + "</td></tr>"
        table += "</table>"
        table += "<br> Docenti assenti: " + update["docentiAssenti"]
        # Send the mail
        sendEmailToUser(user, table, update["sostituzioni"], update["date"], sede, update["classe"])
    print("Done checking " + update["classe"])

def checkUpdates():
    # try:
        sostituzioni = Sostituzioni(fromSedeToURL("margherita"))
        sostituzioni2 = Sostituzioni(fromSedeToURL("turati"))
        sostituzioni3 = Sostituzioni(fromSedeToURL("serale"))

        usersInMargherita = usersDb.find({"endpoint": "margherita"})
        usersInTurati = usersDb.find({"endpoint": "turati"})
        usersInSerale = usersDb.find({"endpoint": "serale"})

        if len(list(usersInMargherita)) == 0 and len(list(usersInTurati)) == 0 and len(list(usersInSerale)) == 0:
            print("No users found in the database")
            return False

        # Get today updates if the hour is between 8 and 14 
        if datetime.now().hour >= 8 and datetime.now().hour <= 14:
            print("Getting today updates")
            updates = sostituzioni.getTodayUpdates()
            updates2 = sostituzioni2.getTodayUpdates()
            updates3 = sostituzioni3.getTodayUpdates()
        else:
            print("Getting next updates")
            updates = sostituzioni.getNextUpdates()
            updates2 = sostituzioni2.getNextUpdates()
            updates3 = sostituzioni3.getNextUpdates()
        
        for update in updates:
            check(update, "margherita")
        for update in updates2:
            check(update, "turati")
        for update in updates3:
            check(update, "serale")
            
        requests.get("https://hc-ping.com/822bf142-8aa4-4621-b3e7-f517ac2bf28f", timeout=10)

        return True
            
    # except Exception as e:
    #     print("Error: unable to fetch data")
    #     print(e)
    #     print(e.__traceback__.tb_lineno)
    #     return False
    
def sendEmailToUser(userDBData, table, array, date, sede, classe):
    email = userDBData["email"]

    # Check if the email has already been sent but if the content is different send it again
    lastSent = userDBData["last_notification"][classe] if classe in userDBData["last_notification"] else datetime.now()
    lastContent = userDBData["last_sostituzioni"][classe] if classe in userDBData["last_sostituzioni"] else ""

    if lastContent == array and lastSent.date() == datetime.now().date():
        print("Email already sent to " + email)
        return False

    else:
        # Send the email
        message = "Ciao, le sostituzioni in data " + date + " della classe " + classe + " (Sede "+sede+") sono state aggiornate: <br> <br>" + table
        sendEmail(email, "Aggiornamento sostituzioni", message, True)

        # Update the last sent date and content: last_notification: {"class": $now} last_sostituzioni: {"class": $array}
        usersDb.update_one({"_id": userDBData["_id"]}, {"$set": {"last_notification." + classe: datetime.now()}})
        usersDb.update_one({"_id": userDBData["_id"]}, {"$set": {"last_sostituzioni." + classe: array}})

        print("Email sent to " + email)
        return True

def main():
    checkUpdates()
    # Close the connection to the database
    client.close()

if __name__ == "__main__":
    main()
