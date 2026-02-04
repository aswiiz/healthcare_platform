import database

def test_registration():
    print("Testing Registration...")
    # Clean up previous test if any
    database.db.users.delete_one({"username": "testuser"})

    # Register user
    success = database.register_user(
        name="Test User",
        age=25,
        phone="+1 555-0199",
        address="123 Test St",
        blood_group="A+",
        username="testuser",
        password="testpassword"
    )
    
    if success:
        print("Registration Success: True")
    else:
        print("Registration Success: False")
        return False

    # Check database
    user = database.check_user("testuser", "testpassword")
    if user and user['name'] == "Test User":
        print("Database Verification: PASSED")
        return True
    else:
        print("Database Verification: FAILED")
        return False

def test_admin_view():
    print("Testing Admin View...")
    users = database.get_all_users()
    if len(users) > 0:
        print(f"Admin View Verification: PASSED ({len(users)} users found)")
        for u in users:
            print(f" - ID: {u['id']}, Name: {u['name']}, Username: {u['username']}")
        return True
    else:
        print("Admin View Verification: FAILED (No users found)")
        return False

if __name__ == "__main__":
    if test_registration():
        test_admin_view()
    else:
        print("Aborting further tests due to registration failure.")
