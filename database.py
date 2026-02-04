import pymongo
from bson.objectid import ObjectId
import os
from datetime import datetime

# Connection setup
# Priority: Environment variable -> Localhost
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.environ.get('MONGO_DB', 'healthcare_platform')

try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    # Test connection
    client.server_info()
except Exception as e:
    print(f"MongoDB Connection Error: {e}")
    # Fallback/Error handle as needed

def mongo_to_dict(doc):
    """Helper to convert MongoDB document to a format compatible with the app's expectations."""
    if doc:
        doc = dict(doc)
        if '_id' in doc:
            doc['id'] = str(doc['_id'])
        return doc
    return None

def init_db():
    """Initialize collections and indexes."""
    try:
        db.users.create_index("username", unique=True)
        db.health_data.create_index("user_id")
        db.bookings.create_index("user_id")
        db.treatments.create_index("user_id")
        db.health_diary.create_index("user_id")
        print("MongoDB initialized with indexes.")
    except Exception as e:
        print(f"Index creation failed: {e}")

def register_user(name, age, gender, phone, address, blood_group, username, password):
    try:
        db.users.insert_one({
            "name": name,
            "age": int(age),
            "gender": gender,
            "phone": phone,
            "address": address,
            "blood_group": blood_group,
            "username": username,
            "password": password,
            "created_at": datetime.utcnow()
        })
        return True
    except pymongo.errors.DuplicateKeyError:
        return False
    except Exception as e:
        print(f"Registration Error: {e}")
        return False

def check_user(username, password):
    user = db.users.find_one({"username": username, "password": password})
    return mongo_to_dict(user)

def get_user_by_id(user_id):
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return mongo_to_dict(user)
    except:
        return None

def get_all_users():
    users = db.users.find()
    return [mongo_to_dict(u) for u in users]

def search_users(query):
    regex_query = {"$regex": query, "$options": "i"}
    users = db.users.find({
        "$or": [
            {"name": regex_query},
            {"phone": regex_query},
            {"username": regex_query}
        ]
    })
    return [mongo_to_dict(u) for u in users]

def save_health_data(user_id, data_dict, analysis):
    try:
        data = {
            "user_id": user_id,
            "analysis_result": analysis,
            "date": datetime.utcnow()
        }
        data.update(data_dict)
        db.health_data.insert_one(data)
        return True
    except Exception as e:
        print(f"Save Health Data Error: {e}")
        return False

def get_health_data(user_id):
    cursor = db.health_data.find({"user_id": user_id}).sort("date", -1)
    return [mongo_to_dict(d) for d in cursor]

def save_booking(user_id, hospital_name, ticket_no, date):
    db.bookings.insert_one({
        "user_id": user_id,
        "hospital_name": hospital_name,
        "ticket_no": ticket_no,
        "date": date,
        "created_at": datetime.utcnow()
    })

def add_treatment(user_id, condition, treatment_plan):
    db.treatments.insert_one({
        "user_id": user_id,
        "condition": condition,
        "treatment_plan": treatment_plan,
        "status": "Ongoing",
        "start_date": datetime.utcnow()
    })

def get_treatments(user_id):
    cursor = db.treatments.find({"user_id": user_id}).sort("start_date", -1)
    return [mongo_to_dict(t) for t in cursor]

def update_health_analysis(record_id, analysis_result):
    try:
        db.health_data.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {"analysis_result": analysis_result}}
        )
        return True
    except:
        return False

def save_diary_entry(user_id, mood, steps, water, sleep, symptoms, note):
    db.health_diary.insert_one({
        "user_id": user_id,
        "mood": mood,
        "steps": int(steps),
        "water_intake": float(water),
        "sleep_hours": float(sleep),
        "symptoms": symptoms,
        "note": note,
        "date": datetime.utcnow()
    })

def get_diary_entries(user_id):
    cursor = db.health_diary.find({"user_id": user_id}).sort("date", -1).limit(30)
    return [mongo_to_dict(e) for e in cursor]

if __name__ == '__main__':
    init_db()
    print("Database switched to MongoDB successfully.")
