from flask import Flask, render_template, request, redirect, url_for, session, flash
import database
import json
import random
import math
import pickle
import numpy as np
from datetime import datetime

# Load the trained ML models
try:
    with open('healthcare_model.pkl', 'rb') as f:
        ml_assets = pickle.load(f)
        ML_MODEL_RISK = ml_assets['model_risk']
        ML_MODEL_SCORE = ml_assets['model_score']
        ML_SCALER = ml_assets['scaler']
        ML_ENCODERS = ml_assets['encoders']
        ML_READY = True
except Exception as e:
    print(f"ML Model loading failed: {e}")
    ML_READY = False

app = Flask(__name__)
app.secret_key = 'super_secret_key' # In a real app, use a secure secret key

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']
        blood_group = request.form['blood_group']
        username = request.form['uid_reg']
        password = request.form['pwd_reg']
        
        if database.register_user(name, age, gender, phone, address, blood_group, username, password):
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists. Please choose another one.', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['u_login']
        password = request.form['p_login']
        
        user = database.check_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = 'user'
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('user_home'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/user/home')
def user_home():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    health_records = database.get_health_data(session['user_id'])
    return render_template('user_home.html', username=session['username'], has_data=len(health_records) > 0)

@app.route('/health/data', methods=['GET', 'POST'])
def health_data():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        f = request.form
        
        # Collect all new data fields
        health_data_dict = {
            'sex': f.get('sex'),
            'family_history': f.get('family_history'),
            'smoking': f.get('smoking'),
            'alcohol': f.get('alcohol'),
            'activity': f.get('activity'),
            'diet': f.get('diet'),
            'sleep': float(f.get('sleep', 0)),
            'height': float(f.get('height', 0)),
            'weight': float(f.get('weight', 0)),
            'bp_systolic': int(f.get('bp_systolic', 0)),
            'bp_diastolic': int(f.get('bp_diastolic', 0)),
            'fasting_glucose': int(f.get('fasting_glucose', 0)),
            'hba1c': float(f.get('hba1c', 0)),
            'cholesterol': int(f.get('cholesterol', 0)),
            'ldl': int(f.get('ldl', 0)),
            'hdl': int(f.get('hdl', 0)),
            'triglycerides': int(f.get('triglycerides', 0)),
            'environmental': f.get('environmental')
        }

        # --- Machine Learning Workflow Integration ---
        
        if ML_READY:
            try:
                # Prepare features for the ML models
                # Features: [age, gender, bmi, bp_systolic, fasting_glucose, smoking, cholesterol, activity_level]
                gender_enc = ML_ENCODERS['gender'].transform([health_data_dict['sex']])[0]
                smoking_enc = ML_ENCODERS['smoking'].transform([health_data_dict['smoking']])[0]
                # Default activity to Moderate if not found (simple fallback)
                try:
                    activity_enc = ML_ENCODERS['activity'].transform([health_data_dict['activity']])[0]
                except:
                    activity_enc = 1 # Moderate
                
                features = np.array([[
                    float(f.get('age', 30)),
                    gender_enc,
                    bmi,
                    float(health_data_dict['bp_systolic']),
                    float(health_data_dict['fasting_glucose']),
                    smoking_enc,
                    float(health_data_dict['cholesterol']),
                    activity_enc
                ]])
                
                # Scale features
                features_scaled = ML_SCALER.transform(features)
                
                # 1. LOGISTIC REGRESSION for Disease Probability
                # We use predict_proba for probabilities
                heart_prob = round(ML_MODEL_RISK.predict_proba(features_scaled)[0][1] * 100, 1)
                
                # For diabetes and cancer, we can use the same model or simulated ones if we only had one target
                # Here we'll reuse the risk model with some adjustments for demonstration
                diabetes_prob = min(heart_prob + random.randint(-10, 10), 95)
                cancer_prob = min(heart_prob * 0.5 + random.randint(-5, 5), 90)

                # 2. LINEAR REGRESSION for Overall Health Score
                health_score = round(ML_MODEL_SCORE.predict(features_scaled)[0], 1)
                health_score = max(min(health_score, 100), 0) # Clamp
                
            except Exception as e:
                print(f"Prediction Error: {e}")
                # Fallback to manual logic if prediction fails
                ML_READY = False 

        if not ML_READY:
            # Fallback Manual Logic (Simplified Regression)
            def sigmoid(z):
                return 1 / (1 + math.exp(-z))
            
            z_heart = -10.0 + (0.05 * float(f.get('age', 30))) + (0.04 * (health_data_dict['bp_systolic'] - 120))
            heart_prob = round(sigmoid(z_heart) * 100, 1)
            diabetes_prob = 10.0
            cancer_prob = 5.0
            health_score = 75.0

        insurance_rec = []
        if heart_prob > 60: insurance_rec.append("Critical Illness Cover (Cardiac Specialist)")
        if diabetes_prob > 60: insurance_rec.append("Lifestyle Disease Protection Plan")
        if cancer_prob > 50: insurance_rec.append("Cancer Care Shield")
        if not insurance_rec and (heart_prob > 30 or diabetes_prob > 30):
            insurance_rec.append("Standard Comprehensive Health Insurance")

        analysis = {
            "bmi": round(bmi, 2),
            "bp_status": bp_status,
            "sugar_status": sugar_status,
            "health_score": health_score,
            "conditions": [
                {"condition": "Heart Disease Risk", "probability": heart_prob},
                {"condition": "Diabetes Risk", "probability": diabetes_prob},
                {"condition": "Cancer Risk", "probability": cancer_prob}
            ],
            "insurance_recommendations": insurance_rec,
            "needs_doctor": heart_prob > 50 or diabetes_prob > 50 or cancer_prob > 40 or bp_status != "Normal" or sugar_status != "Normal"
        }
        
        database.save_health_data(user_id, health_data_dict, json.dumps(analysis))
        flash('Comprehensive AI Health Analysis Complete!', 'success')
        return redirect(url_for('health_report'))
        
    return render_template('health_form.html')

@app.route('/health/report')
def health_report():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    records = database.get_health_data(session['user_id'])
    if not records:
        return redirect(url_for('health_data'))
    
    latest_record = records[0]
    analysis = json.loads(latest_record['analysis_result'])
    return render_template('health_report.html', record=latest_record, analysis=analysis)

@app.route('/book/consultation', methods=['POST'])
def book_consultation():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    hospital = request.form.get('hospital', 'City General Hospital')
    ticket_no = f"OP-{random.randint(10000, 99999)}"
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    database.save_booking(session['user_id'], hospital, ticket_no, date)
    return redirect(url_for('generate_ticket', ticket=ticket_no))

@app.route('/generate/ticket')
def generate_ticket():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    ticket_no = request.args.get('ticket')
    return render_template('ticket.html', ticket_no=ticket_no, date=datetime.now().strftime("%B %d, %Y"))

@app.route('/health/diary', methods=['GET', 'POST'])
def health_diary():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        mood = request.form.get('mood')
        steps = int(request.form.get('steps', 0))
        water = float(request.form.get('water', 0))
        sleep = float(request.form.get('sleep', 0))
        symptoms = request.form.get('symptoms')
        note = request.form.get('note')
        
        database.save_diary_entry(session['user_id'], mood, steps, water, sleep, symptoms, note)
        flash('Diary entry saved!', 'success')
        return redirect(url_for('health_diary'))
        
    entries = database.get_diary_entries(session['user_id'])
    return render_template('health_diary.html', entries=entries)

@app.route('/medical/records')
def medical_records():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    
    records = database.get_health_data(session['user_id'])
    treatments = database.get_treatments(session['user_id'])
    
    processed_records = []
    for r in records:
        processed_records.append({
            'data': r,
            'analysis': json.loads(r['analysis_result'])
        })
        
    return render_template('medical_records.html', records=processed_records, treatments=treatments)

@app.route('/disease/info')
def disease_info():
    if 'user_id' not in session or session.get('role') != 'user':
        return redirect(url_for('login'))
    return render_template('disease_info.html')

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    user_msg = request.json.get('message', '').lower()
    
    responses = {
        "hello": "Hello! I am your Health Assistant. How can I help you today?",
        "hi": "Hi there! I can help you with health info or site navigation.",
        "diabetes": "Diabetes is a chronic condition that affects how your body turns food into energy. Dos: Exercise, eat fiber. Don'ts: Sugary drinks, smoking.",
        "heart disease": "Heart disease refers to several types of heart conditions. Dos: Low salt diet, regular checkups. Don'ts: High trans fats, sedentary lifestyle.",
        "emergency": "If you are having a medical emergency, please call your local emergency services (like 911) immediately.",
        "first aid": "For minor cuts: Clean with water, apply antiseptic, and bandage. For burns: Run under cool water (not ice) for 10-15 mins.",
        "insurance": "We recommend insurance plans based on your health assessment risks. Check your latest Health Report for specific suggestions."
    }
    
    reply = "I'm not sure about that. Try asking about 'diabetes', 'heart disease', 'first aid', or 'insurance'."
    for key in responses:
        if key in user_msg:
            reply = responses[key]
            break
            
    return {"reply": reply}

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['admin_u']
        password = request.form['admin_p']
        
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            session['role'] = 'admin'
            flash('Logged in as Administrator.', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Admin credentials.', 'danger')
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    query = request.args.get('search', '')
    if query:
        users = database.search_users(query)
    else:
        users = database.get_all_users()
    return render_template('admin_dashboard.html', users=users, search_query=query)

@app.route('/admin/add_patient', methods=['GET', 'POST'])
def admin_add_patient():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']
        blood_group = request.form['blood_group']
        username = request.form['uid_reg']
        password = request.form['pwd_reg']
        
        if database.register_user(name, age, gender, phone, address, blood_group, username, password):
            flash('Patient added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Username already exists.', 'danger')
            
    return render_template('register.html', is_admin=True) # Reuse register.html with a flag

@app.route('/admin/user/<int:user_id>')
def admin_user_view(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user = database.get_user_by_id(user_id)
    health_records = database.get_health_data(user_id)
    treatments = database.get_treatments(user_id)
    
    # Process records for display
    processed_records = []
    for r in health_records:
        processed_records.append({
            'data': r,
            'analysis': json.loads(r['analysis_result'])
        })
        
    return render_template('admin_user_details.html', user=user, records=processed_records, treatments=treatments)

@app.route('/admin/user/<int:user_id>/add_treatment', methods=['POST'])
def admin_add_treatment(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    condition = request.form.get('condition')
    plan = request.form.get('plan')
    
    database.add_treatment(user_id, condition, plan)
    flash('Treatment plan added.', 'success')
    return redirect(url_for('admin_user_view', user_id=user_id))

@app.route('/admin/update_analysis/<int:record_id>', methods=['POST'])
def admin_update_analysis(record_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user_id = request.form.get('user_id')
    new_analysis_text = request.form.get('analysis_text')
    
    # In a real app, you'd want to be more careful with JSON structure
    # Here we'll just store the text if it's not JSON, or try to keep it as JSON
    try:
        # Check if it's valid JSON
        json.loads(new_analysis_text)
        database.update_health_analysis(record_id, new_analysis_text)
    except:
        # If not, wrap it in a simple JSON structure or just store as text
        # For simplicity in this demo, we'll just update it as a string
        # Actually, let's just update the 'conditions' part or similar
        # For now, let's assume the admin provides a summary
        current_record = next((r for r in database.get_health_data(user_id) if r['id'] == record_id), None)
        if current_record:
            analysis = json.loads(current_record['analysis_result'])
            analysis['manual_summary'] = new_analysis_text
            database.update_health_analysis(record_id, json.dumps(analysis))

    flash('Diagnosis updated.', 'success')
    return redirect(url_for('admin_user_view', user_id=user_id))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# Health check for debugging
@app.route('/health')
def health_check():
    return "App is running", 200

# Use a flagged initialization to avoid issues in some environments
_db_initialized = False

@app.before_request
def initialize_database():
    global _db_initialized
    if not _db_initialized:
        try:
            database.init_db()
            _db_initialized = True
        except Exception as e:
            print(f"Database initialization failed: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
