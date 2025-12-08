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

    def delete_class_from_user(self, email, classe):
        # Delete where classe is in classi array
        self.users_collection.update_one({"email": email}, {"$pull": {"classi": classe}})
        return True

    def add_class_to_user(self, email, classe):
        # Add where classe is in classi array
        self.users_collection.update_one({"email": email}, {"$push": {"classi": classe}})
        return True

    def update_telegram_chat_id(self, email, chat_id):
        self.users_collection.update_one({"email": email}, {"$set": {"telegram_chat_id": chat_id}})
        return True

    def update_fuzzy_matching(self, email, fuzzy_matching):
        self.users_collection.update_one({"email": email}, {"$set": {"fuzzy_teacher_matching": fuzzy_matching}})
        return True

    def add_teacher_to_user(self, email, teacher):
        self.users_collection.update_one({"email": email}, {"$push": {"watched_teachers": teacher}})
        return True

    def delete_teacher_from_user(self, email, teacher):
        self.users_collection.update_one({"email": email}, {"$pull": {"watched_teachers": teacher}})
        return True

    def insert_user(self, email, classi):
        user = User(email=email, classi=classi)
        self.users_collection.insert_one(user.model_dump(by_alias=True, exclude={"id"}))

    def get_users_by_endpoint(self, endpoint):
        users = self.users_collection.find({"endpoint": endpoint})
        return [User(**user) for user in users]

    def update_user_one(self, filter_query, update_query):
        self.users_collection.update_one(filter_query, update_query)

    def close(self):
        self.client.close()


