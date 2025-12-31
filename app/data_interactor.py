from contact import Contact
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId


class DataInteractor:
    def __init__(self, database_name, collection_name):
        self._connection = None
        self.config = {
            "host": 'localhost',
            "port": 27017,
        }
        self.database_name = database_name
        self.collection_name = collection_name

    def _get_connection(self):
        if self._connection is not None:
            return self._connection
        try:
            self._connection = MongoClient(**self.config)
            return self._connection
        except ConnectionFailure as e:
            print(f"Connection Error: {e}")
            return None

    def close_connection(self):
        if self._connection is not None:
            try:
                self._connection.close()
                self._connection = None
            except Exception as e:
                print(f"Closing Connection Error: {e}")

    def create_contact(self, contact_data: dict):
        conn = self._get_connection()
        if not conn:
            return None
        db = conn[self.database_name]
        collection = db[self.collection_name]

        try:
            exist = collection.find_one({"phone_number": contact_data["phone_number"]})
            if exist is not None:
                print(f"The phone number {contact_data['phone_number']} already exists!!!")
                return None
            result = collection.insert_one(contact_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating contact: {e}")
            return None
        finally:
            self.close_connection()

    def get_all_contacts(self):
        conn = self._get_connection()
        if not conn:
            return []

        db = conn[self.database_name]
        collection = db[self.collection_name]
        try:
            contacts = collection.find().to_list()
            return [Contact.from_dict(contact).to_dict() for contact in contacts]
        finally:
            self.close_connection()

    def update_contact(self, contact_id: str, contact_data: dict) -> bool:
        conn = self._get_connection()
        if not conn:
            return False

        db = conn[self.database_name]
        collection = db[self.collection_name]

        try:
            if "phone_number" in contact_data.keys():
                exist = collection.find_one({"phone_number": contact_data["phone_number"]})
                if exist is not None:
                    print(f"The phone number {contact_data['phone_number']} already exists!!!")
                    return False
            result = collection.update_one({'_id': ObjectId(contact_id)}, {"$set": contact_data})
            return result.matched_count > 0
        except Exception as e:
            print(f"Update Error: {e}")
            return False
        finally:
            self.close_connection()

    def delete_contact(self, contact_id: str) -> bool:
        conn = self._get_connection()
        if conn is None:
            return False

        db = conn[self.database_name]
        collection = db[self.collection_name]
        try:
            result = collection.delete_one({"_id": ObjectId(contact_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Delete Error: {e}")
            return False
        finally:
            self.close_connection()
