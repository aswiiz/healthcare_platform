from flask import Flask, render_template, request, redirect, url_for, session, flash
import database
import json
import random
from datetime import datetime

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
            'waist': float(f.get('waist', 0)),
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

        # --- Enhanced AI Simulation Logic ---
        heart_prob = 10
        diabetes_prob = 10
        cancer_prob = 5
        
        bmi = health_data_dict['weight'] / ((health_data_dict['height']/100)**2)
        
        # Heart Disease Logic
        if health_data_dict['bp_systolic'] > 140: heart_prob += 20
        if health_data_dict['smoking'] == 'Yes': heart_prob += 25
        if health_data_dict['cholesterol'] > 240: heart_prob += 15
        if 'heart' in health_data_dict['family_history'].lower(): heart_prob += 20
        if bmi > 30: heart_prob += 10
        
        # Diabetes Logic
        if health_data_dict['fasting_glucose'] > 126: diabetes_prob += 40
        if health_data_dict['hba1c'] > 6.5: diabetes_prob += 45
        if 'diabetes' in health_data_dict['family_history'].lower(): diabetes_prob += 15
        if health_data_dict['waist'] > (102 if health_data_dict['sex'] == 'Male' else 88): diabetes_prob += 15
        
        # Cancer Logic
        if health_data_dict['smoking'] == 'Yes': cancer_prob += 30
        if 'cancer' in health_data_dict['family_history'].lower(): cancer_prob += 20
        if health_data_dict['environmental'] == 'High': cancer_prob += 15
        if health_data_dict['diet'] == 'Poor': cancer_prob += 10
        
        # Cap probabilities at 95%
        heart_prob = min(heart_prob + random.randint(-5, 5), 95)
        diabetes_prob = min(diabetes_prob + random.randint(-5, 5), 95)
        cancer_prob = min(cancer_prob + random.randint(-5, 5), 95)

        analysis = {
            "bmi": round(bmi, 2),
            "conditions": [
                {"condition": "Heart Disease Risk", "probability": heart_prob},
                {"condition": "Diabetes Risk", "probability": diabetes_prob},
                {"condition": "Cancer Risk", "probability": cancer_prob}
            ],
            "needs_doctor": heart_prob > 50 or diabetes_prob > 50 or cancer_prob > 40
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
    
    users = database.get_all_users()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/user/<int:user_id>')
def admin_user_view(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user = database.get_user_by_id(user_id)
    health_records = database.get_health_data(user_id)
    
    # Process records for display
    processed_records = []
    for r in health_records:
        processed_records.append({
            'data': r,
            'analysis': json.loads(r['analysis_result'])
        })
        
    return render_template('admin_user_details.html', user=user, records=processed_records)

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
