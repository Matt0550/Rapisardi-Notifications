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
client = MongoClient(MONGODB_HOST, MONGODB_PORT, username=MONGODB_USERNAME, password=MONGODB_PASSWORD, authSource=MONGODB_DATABASE)
db = client[MONGODB_DATABASE]
usersDb = db.users

# Print all the users
for user in usersDb.find():
    print(user)

# Setup SMTP server
SMTP_SERVER = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USERNAME")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

# Check if the SMTP password is set
if SMTP_PASSWORD == None or SMTP_PASSWORD == "":
    print("SMTP password not set")
    exit()

def sendEmail(to, subject, body, html=False):
    # Edit the mittent

    msg = MIMEMultipart()
    msg["From"] = "Rapisardi Updates <" + SMTP_USER + ">"
    msg["To"] = to
    msg["Subject"] = subject

    if html:
        msg.attach(MIMEText(body, "html"))
    else:
        msg.attach(MIMEText(body, "plain"))
    text = msg.as_string()
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(SMTP_USER, to, text)
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
            userClass = usersDb.find({"classe": update["classe"]})
            for user in userClass:
                print(user)

            if len(list(userClass)) == 0:
                print("No users found for " + update["classe"])
                continue
            
            for user in userClass:
                print("Checking " + update["classe"] + " for " + userClass)

                if update["classe"].lower() != userClass.lower():
                    continue

                print("Found update for " + userClass)
                # Make a table with the data
                table = "<table><tr><th>Ora</th><th>Sostituzione</th></tr>"
                for i in range(len(update["ore"])):
                    table += "<tr><td>" + update["ore"][i] + "</td><td>" + update["sostituzioni"][i] + "</td></tr>"
                table += "</table>"
                # Send the mail
                sendEmailToUser(user, user["email"], table, update["sostituzioni"], update["date"], userClass)
        return True
            
    except Exception as e:
        print("Error: unable to fetch data")
        print(e)
        return None
    
def sendEmailToUser(userDBData, email, table, array, date, userClass):
    print(array)
    lastSent = userDBData[2]
    lastContent = userDBData[3]

    # Check if the email has already been sent but if the content is different send it again
    if lastSent.strftime("%Y-%m-%d") == datetime.now().strftime("%Y-%m-%d") and lastContent == str(array):
        print("Email already sent")
        return None
    else:
        # Send the email
        message = "Ciao, le sostituzioni in data " + date + " della classe " + userClass + " sono state aggiornate: <br> <br>" + table
        sendEmail(email, "Aggiornamento sostituzioni", message, True)

        # Update the last sent date and content
        sql = 'UPDATE users SET last_notification = "' + str(datetime.now()) + '", last_sostituzioni = "' + str(array) + '" WHERE id = ' + str(userDBData[0]) + ';'
        try:
            cursor.execute(sql)
            db.commit()
            print("Updated user " + str(userDBData[0]))
            return True
        except Exception as e:
            print("Error: unable to update user")
            print(e)
            return None

def main():
    try:
        requests.get("https://hc-ping.com/822bf142-8aa4-4621-b3e7-f517ac2bf28f", timeout=10)
    except requests.RequestException as e:
        # Log ping failure here...
        print("Ping failed: %s" % e)
    checkUpdates()

if __name__ == "__main__":
    main()