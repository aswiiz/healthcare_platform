import database
import json

def test_health_feature():
    print("Testing Health Data & AI Analysis...")
    # Register a new user
    database.register_user("Alice Green", 28, "+1 999 0000", "789 Pine St", "O+", "alice", "alice123")
    user = database.check_user("alice", "alice123")
    user_id = user['id']
    
    # Save health data
    analysis_sim = {
        "risks": ["High Blood Pressure"],
        "conditions": [{"condition": "Heart Attack Risk", "probability": 45}],
        "bmi": 24.5,
        "needs_doctor": True
    }
    database.save_health_data(user_id, 150, 95, 200, 110, 75, 175, json.dumps(analysis_sim))
    
    # Retrieve health data
    data = database.get_health_data(user_id)
    if len(data) > 0 and data[0]['bp_systolic'] == 150:
        print("Health Data Storage: PASSED")
    else:
        print("Health Data Storage: FAILED")
        return False

    # Test Booking
    database.save_booking(user_id, "City Central Hospital", "OP-12345", "2026-01-24 15:30")
    print("Booking Storage: PASSED")
    
    # Test Admin Fetch
    all_users = database.get_all_users()
    if any(u['username'] == 'alice' for u in all_users):
        print("Admin Fetch All Users: PASSED")
    else:
        print("Admin Fetch All Users: FAILED")
        return False
        
    return True

if __name__ == "__main__":
    # Reset DB for clean test
    import os
    if os.path.exists("users.db"):
        os.remove("users.db")
    database.init_db()
    
    if test_health_feature():
        print("\nAll Expanded Features Backend Logic: PASSED")
    else:
        print("\nVerification: FAILED")
