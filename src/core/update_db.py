"""
This script is used to send email with the updates of the substitutions to the users that have subscribed to the service
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import requests

from core.config import settings
from core.db import Database
from core.logger_base import logger
from scrapers.sostituzioni import Sostituzioni

from jinja2 import Environment, FileSystemLoader
from bson import ObjectId

class Updater:
    def __init__(self):
        self.db = Database()
        self.template_env = Environment(loader=FileSystemLoader("src/api/templates"))
        if not settings.SMTP_PASSWORD:
            logger.warning("SMTP password not set")

    def send_email(self, to, subject, body, html=False):
        msg = MIMEMultipart()
        msg["From"] = f"Rapisardi Notifications <{settings.SMTP_FROM}>"
        msg["To"] = to
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))
        
        text = msg.as_string()
        
        try:
            if str(settings.SMTP_SSL).lower() == "true":
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, to, text)
            server.quit()
        except Exception as e:
            logger.error(f"Error sending email: {e}")

    def send_telegram_message(self, chat_id, message):
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.warning("Telegram bot token not set")
            return

        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, data=data)
        except Exception as e:
            logger.error(f"Error sending telegram message: {e}")

    def from_sede_to_url(self, sede):
        if sede == "margherita":
            return settings.SOSTITUZIONI_MARGHERITA_URL
        elif sede == "turati":
            return settings.SOSTITUZIONI_TURATI_URL
        elif sede == "serale":
            return settings.SOSTITUZIONI_SERALE_URL
        else:
            return settings.SOSTITUZIONI_MARGHERITA_URL

    def adapt_db_user(self, user):
        # Since we are using Pydantic models, defaults are already set.
        # We just need to ensure last_sostituzioni and last_notification keys match subscriptions.
        
        needs_update = False
        
        last_sostituzioni = user.last_sostituzioni
        last_notification = user.last_notification
        classi = user.classi
        watched_teachers = user.watched_teachers
        
        # Clean up old keys
        all_keys = set(classi) | set(watched_teachers)
        
        for key in all_keys:
            if key not in last_sostituzioni:
                last_sostituzioni[key] = ""
                needs_update = True
            if key not in last_notification:
                last_notification[key] = datetime.now()
                needs_update = True
        
        for key in list(last_sostituzioni.keys()):
            if key not in all_keys:
                del last_sostituzioni[key]
                needs_update = True
        for key in list(last_notification.keys()):
            if key not in all_keys:
                del last_notification[key]
                needs_update = True
                
        if needs_update:
            self.db.update_user_one({"_id": ObjectId(user.id)}, {
                "$set": {
                    "last_notification": last_notification,
                    "last_sostituzioni": last_sostituzioni
                }
            })
            user.last_notification = last_notification
            user.last_sostituzioni = last_sostituzioni

    def check_update_for_user(self, update, user, sede):
        logger.info(f"Checking {update['classe']} for {user.email}")
        self.adapt_db_user(user)
        
        # Prepare data for template
        table_rows = []
        for i in range(len(update["ore"])):
            table_rows.append({
                "ora": update["ore"][i],
                "sostituzione": update["sostituzioni"][i],
                "classe": update["classe"]
            })
            
        template = self.template_env.get_template("email_notification.html")
        html_content = template.render(
            message_intro=f"Le sostituzioni della classe {update['classe']} sono state aggiornate.",
            date=update["date"],
            sede=sede,
            table_rows=table_rows,
            show_class=False,
            docenti_assenti=update["docentiAssenti"]
        )
        
        self.send_email_to_user(user, html_content, update["sostituzioni"], update["date"], sede, update["classe"], f"Aggiornamento classe {update['classe']}")
        
        if user.telegram_chat_id:
            telegram_message = f"<b>Aggiornamento sostituzioni</b>\n\nData: {update['date']}\nClasse: {update['classe']} ({sede})\n\n"
            for i in range(len(update["ore"])):
                telegram_message += f"<b>{update['ore'][i]}</b>: {update['sostituzioni'][i]}\n"
            telegram_message += f"\nDocenti assenti: {update['docentiAssenti']}"
            
            self.send_telegram_message(user.telegram_chat_id, telegram_message)

    def check_teacher_update_for_user(self, user, teacher, updates, docenti_assenti, date, sede):
        logger.info(f"Checking teacher {teacher} for {user.email}")
        self.adapt_db_user(user)
        
        found_updates = []
        is_absent = teacher.lower() in docenti_assenti.lower()
        
        for update in updates:
            for i, sost in enumerate(update["sostituzioni"]):
                if teacher.lower() in sost.lower():
                    found_updates.append({
                        "ora": update["ore"][i],
                        "sostituzione": sost,
                        "classe": update["classe"]
                    })
        
        if not found_updates and not is_absent:
            return

        # Generate unique content hash for comparison
        content_hash = str(found_updates) + str(is_absent)
        
        template = self.template_env.get_template("email_notification.html")
        message_intro = f"Ci sono aggiornamenti per il docente {teacher}."
        if is_absent:
            message_intro += " Il docente risulta ASSENTE."
            
        html_content = template.render(
            message_intro=message_intro,
            date=date,
            sede=sede,
            table_rows=found_updates,
            show_class=True,
            docenti_assenti=docenti_assenti if is_absent else None
        )
        
        subject = f"Aggiornamento docente {teacher}"
        if is_absent:
            subject += " (ASSENTE)"
            
        self.send_email_to_user(user, html_content, content_hash, date, sede, teacher, subject)
        
        if user.telegram_chat_id:
            telegram_message = f"<b>{subject}</b>\n\nData: {date} ({sede})\n"
            if is_absent:
                telegram_message += f"\n⚠️​ <b>Il docente {teacher} risulta ASSENTE</b>\n"
            
            if found_updates:
                telegram_message += "\n<b>Sostituzioni trovate:</b>\n"
                for item in found_updates:
                    telegram_message += f"Classe {item['classe']} - {item['ora']} ora: {item['sostituzione']}\n"
            
            self.send_telegram_message(user.telegram_chat_id, telegram_message)

    def send_email_to_user(self, user_data, html_content, content_hash, date, sede, key, subject):
        email = user_data.email
        last_notification = user_data.last_notification
        last_sostituzioni = user_data.last_sostituzioni
        
        last_sent = last_notification.get(key, datetime.now())
        last_content = last_sostituzioni.get(key, "")
        
        # If content is list (from class update), convert to string for comparison
        if isinstance(content_hash, list):
            content_hash = str(content_hash)
        if isinstance(last_content, list):
            last_content = str(last_content)

        if last_content == content_hash and last_sent.date() == datetime.now().date():
            logger.info(f"Email already sent to {email} for {key}")
            return False
        
        self.send_email(email, subject, html_content, True)
        
        self.db.update_user_one({"_id": ObjectId(user_data.id)}, {
            "$set": {
                f"last_notification.{key}": datetime.now(),
                f"last_sostituzioni.{key}": content_hash
            }
        })
        logger.info(f"Email sent to {email} for {key}")
        return True

    def check_updates(self):
        sedi = ["margherita", "turati", "serale"]
        
        total_users = 0
        for sede in sedi:
            users = list(self.db.get_users_by_endpoint(sede))
            total_users += len(users)
            
        if total_users == 0:
            logger.warning("No users found in the database")
            return False

        now = datetime.now()
        get_today = 8 <= now.hour <= 14
        logger.info(f"Getting {'today' if get_today else 'next'} updates")

        for sede in sedi:
            url = self.from_sede_to_url(sede)
            scraper = Sostituzioni(url)
            
            try:
                if get_today:
                    updates = scraper.getTodayUpdates()
                else:
                    updates = scraper.getNextUpdates()
                
                if not updates:
                    continue

                # Get docenti assenti from the first update (it's the same for all)
                docenti_assenti = updates[0]["docentiAssenti"]
                date = updates[0]["date"]

                # 2. Check for teacher updates
                # Find users who have watched_teachers not empty
                # Since we are iterating over all users anyway (get_users_by_endpoint), we can just check the user object
                # But wait, the previous loop was iterating over updates, not users.
                
                # Let's iterate over all users for this endpoint once
                users = list(self.db.get_users_by_endpoint(sede))
                
                for user in users:
                    # Check class updates
                    for update in updates:
                        if update["classe"] in user.classi:
                            self.check_update_for_user(update, user, sede)
                    
                    # Check teacher updates
                    if user.watched_teachers:
                        for teacher in user.watched_teachers:
                            self.check_teacher_update_for_user(user, teacher, updates, docenti_assenti, date, sede)

            except Exception as e:
                logger.error(f"Error fetching updates for {sede}: {e}")
                import traceback
                traceback.print_exc()

        try:
            requests.get(settings.HEALTHCHECK_URL, timeout=10)
        except Exception:
            pass
            
        return True

    def close(self):
        self.db.close()

def checkUpdates():
    updater = Updater()
    try:
        updater.check_updates()
    finally:
        updater.close()

if __name__ == "__main__":
    checkUpdates()

