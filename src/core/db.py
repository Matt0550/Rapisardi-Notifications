"""
Database module for handling MongoDB operations.
"""
from pymongo import MongoClient
from core.config import settings
from core.models import User

class Database:
    def __init__(self):
        # Connect to the database
        self.client = MongoClient(
            f"mongodb+srv://{settings.MONGODB_USERNAME}:{settings.MONGODB_PASSWORD}@{settings.MONGODB_HOST}"
        )
        self.db = self.client[settings.MONGODB_DATABASE]
        self.users_collection = self.db.users

    def get_user_by_email(self, email) -> User | None:
        data = self.users_collection.find_one({"email": email})
        if data:
            return User(**data)
        return None

    def delete_class_from_user(self, email, classe, sede="margherita"):
        # Delete where classe is in classi array
        # We need to match both name and sede
        self.users_collection.update_one(
            {"email": email}, 
            {"$pull": {"classi": {"name": classe, "sede": sede}}}
        )
        # Also try to remove legacy string format just in case
        self.users_collection.update_one({"email": email}, {"$pull": {"classi": classe}})
        return True

    def add_class_to_user(self, email, classe, sede="margherita"):
        # Add where classe is in classi array
        # Check if already exists
        user = self.get_user_by_email(email)
        if user:
            for c in user.classi:
                if c.name == classe and c.sede == sede:
                    return True # Already exists

        self.users_collection.update_one(
            {"email": email}, 
            {"$push": {"classi": {"name": classe, "sede": sede}}}
        )
        return True

    def update_telegram_chat_id(self, email, chat_id):
        self.users_collection.update_one({"email": email}, {"$set": {"telegram_chat_id": chat_id}})
        return True

    def update_fuzzy_matching(self, email, fuzzy_matching):
        self.users_collection.update_one({"email": email}, {"$set": {"fuzzy_teacher_matching": fuzzy_matching}})
        return True

    def add_teacher_to_user(self, email, teacher, sede="margherita"):
        user = self.get_user_by_email(email)
        if user:
            for t in user.watched_teachers:
                if t.name == teacher and t.sede == sede:
                    return True

        self.users_collection.update_one(
            {"email": email}, 
            {"$push": {"watched_teachers": {"name": teacher, "sede": sede}}}
        )
        return True

    def delete_teacher_from_user(self, email, teacher, sede="margherita"):
        self.users_collection.update_one(
            {"email": email}, 
            {"$pull": {"watched_teachers": {"name": teacher, "sede": sede}}}
        )
        # Also try to remove legacy string format
        self.users_collection.update_one({"email": email}, {"$pull": {"watched_teachers": teacher}})
        return True

    def insert_user(self, email, classi):
        # classi is expected to be a list of dicts now, or strings
        # If strings, we assume margherita
        new_classi = []
        for c in classi:
            if isinstance(c, str):
                new_classi.append({"name": c, "sede": "margherita"})
            else:
                new_classi.append(c)
                
        user = User(email=email, classi=new_classi)
        self.users_collection.insert_one(user.model_dump(by_alias=True, exclude={"id"}))

    def delete_user(self, email):
        result = self.users_collection.delete_one({"email": email})
        return result.deleted_count > 0

    def get_users_interested_in_sede(self, sede):
        # Find users who have at least one class or teacher in this sede
        # OR users who have the legacy endpoint set to this sede (and might have legacy string subscriptions)
        users = self.users_collection.find({
            "$or": [
                {"classi.sede": sede},
                {"watched_teachers.sede": sede},
                {"endpoint": sede} # For legacy support
            ]
        })
        return [User(**user) for user in users]

    def get_users_by_endpoint(self, endpoint):
        # Deprecated, use get_users_interested_in_sede
        return self.get_users_interested_in_sede(endpoint)

    def update_user_one(self, filter_query, update_query):
        self.users_collection.update_one(filter_query, update_query)

    def close(self):
        self.client.close()


