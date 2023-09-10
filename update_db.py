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
    
def checkUpdates():
    try:
        sostituzioni = Sostituzioni("https://www.rapisardidavinci.edu.it/sost/app/sostituzioni.php")
        # Get today updates if the hour is between 8 and 14 
        if datetime.now().hour >= 8 and datetime.now().hour <= 14:
            updates = sostituzioni.getTodayUpdates()
        else:
            updates = sostituzioni.getNextUpdates()
        
        for update in updates:
            print("Checking update for " + update["classe"])
            # Search users where the class is the same as the update 
            usersInClass = usersDb.find({"classe": update["classe"]})      
            for user in usersInClass:

                # if len(list(usersInClass)) == 0:
                #     print("No users found for " + update["classe"] + " in the database")
                #     continue

                print("Checking " + update["classe"] + " for " + user["email"])

                if update["classe"].lower() != user["classe"].lower():
                    continue

                print("Found update for " + user["email"])
                # Make a table with the data
                table = "<table><tr><th>Ora</th><th>Sostituzione</th></tr>"
                for i in range(len(update["ore"])):
                    table += "<tr><td>" + update["ore"][i] + "</td><td>" + update["sostituzioni"][i] + "</td></tr>"
                table += "</table>"
                table += "<br> Docenti assenti: " + update["docentiAssenti"]
                # Send the mail
                sendEmailToUser(user, table, update["sostituzioni"], update["date"])

        requests.get("https://hc-ping.com/822bf142-8aa4-4621-b3e7-f517ac2bf28f", timeout=10)

        return True
            
    except Exception as e:
        print("Error: unable to fetch data")
        print(e)
        print(e.__traceback__.tb_lineno)
        return None
    
def sendEmailToUser(userDBData, table, array, date):
    lastSent = userDBData["last_notification"] if "last_notification" in userDBData else datetime.now()
    lastContent = userDBData["last_sostituzioni"] if "last_sostituzioni" in userDBData else ""

    email = userDBData["email"]
    userClass = userDBData["classe"]

    # Check if the email has already been sent but if the content is different send it again
    if lastSent.strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d") and lastContent == str(array):
        print("Email already sent")
        return None
    else:
        # Send the email
        message = "Ciao, le sostituzioni in data " + date + " della classe " + userClass + " (Sede Viale R. Margherita) sono state aggiornate: <br> <br>" + table
        sendEmail(email, "Aggiornamento sostituzioni", message, True)

        # Update the last sent date and content
        usersDb.update_one({"_id": userDBData["_id"]}, {"$set": {"last_notification": datetime.now(), "last_sostituzioni": str(array)}})
        print("Email sent to " + email)
        return True



def main():
    checkUpdates()

if __name__ == "__main__":
    main()