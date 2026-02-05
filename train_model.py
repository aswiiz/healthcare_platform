import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
import pickle
import os

# 1. LOAD HEALTHCARE DATASET (Sourcing synthetic data for demo)
def generate_synthetic_data(n_samples=2000):
    np.random.seed(42)
    data = {
        'age': np.random.randint(18, 90, n_samples),
        'gender': np.random.choice(['Male', 'Female'], n_samples),
        'bmi': np.random.uniform(15, 45, n_samples),
        'bp_systolic': np.random.randint(90, 180, n_samples),
        'fasting_glucose': np.random.randint(70, 250, n_samples),
        'smoking': np.random.choice(['Yes', 'No'], n_samples),
        'cholesterol': np.random.randint(120, 300, n_samples),
        'activity_level': np.random.choice(['Sedentary', 'Moderate', 'Active'], n_samples),
        'stress_level': np.random.choice(['Low', 'Moderate', 'High'], n_samples),
        'mood': np.random.choice(['Happy', 'Anxious', 'Sad', 'Stressed'], n_samples),
        'sleep_quality': np.random.choice(['Restful', 'Interrupted', 'Insomnia'], n_samples),
        'lifestyle_balance': np.random.choice(['Great', 'Good', 'Poor'], n_samples),
        'heart_risk': np.random.randint(0, 2, n_samples), # Target for Logistic Regression
        'health_score': np.random.uniform(0, 100, n_samples) # Target for Linear Regression
    }
    
    df = pd.DataFrame(data)
    
    # Introduce some logic to make the data learnable
    df.loc[df['bp_systolic'] > 140, 'heart_risk'] = 1
    df.loc[df['smoking'] == 'Yes', 'heart_risk'] = 1
    df.loc[df['bmi'] > 30, 'health_score'] -= 20
    df.loc[df['bp_systolic'] > 140, 'health_score'] -= 15
    df['health_score'] = df['health_score'].clip(0, 100)
    
    return df

print("Step 1: Loading Dataset...")
df = generate_synthetic_data()

# 2. PREPROCESS DATA
print("Step 2: Preprocessing (Encoding & Scaling)...")
le_gender = LabelEncoder()
df['gender'] = le_gender.fit_transform(df['gender'])

le_smoking = LabelEncoder()
df['smoking'] = le_smoking.fit_transform(df['smoking'])

le_activity = LabelEncoder()
df['activity_level'] = le_activity.fit_transform(df['activity_level'])

le_stress = LabelEncoder()
df['stress_level'] = le_stress.fit_transform(df['stress_level'])

le_mood = LabelEncoder()
df['mood'] = le_mood.fit_transform(df['mood'])

le_sleep_q = LabelEncoder()
df['sleep_quality'] = le_sleep_q.fit_transform(df['sleep_quality'])

le_balance = LabelEncoder()
df['lifestyle_balance'] = le_balance.fit_transform(df['lifestyle_balance'])

# Define Features
X = df[['age', 'gender', 'bmi', 'bp_systolic', 'fasting_glucose', 'smoking', 'cholesterol', 'activity_level', 'stress_level', 'mood', 'sleep_quality', 'lifestyle_balance']]
y_risk = df['heart_risk']
y_score = df['health_score']

# Train Test Split
X_train, X_test, y_train_risk, y_test_risk = train_test_split(X, y_risk, test_size=0.2, random_state=42)
_, _, y_train_score, y_test_score = train_test_split(X, y_score, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. TRAIN REGRESSION MODELS
print("Step 3: Training Models...")
# Logistic Regression for Risk
model_risk = LogisticRegression()
model_risk.fit(X_train_scaled, y_train_risk)

# Linear Regression for Health Score
model_score = LinearRegression()
model_score.fit(X_train_scaled, y_train_score)

# 4. EVALUATE MODELS
print("Step 4: Evaluating Accuracy...")
risk_preds = model_risk.predict(X_test_scaled)
risk_acc = accuracy_score(y_test_risk, risk_preds)
print(f"Logistic Regression Accuracy (Risk): {risk_acc * 100:.2f}%")

score_preds = model_score.predict(X_test_scaled)
score_mse = mean_squared_error(y_test_score, score_preds)
print(f"Linear Regression MSE (Score): {score_mse:.4f}")

# 5. SAVE BEST MODELS USING PICKLE
print("Step 5: Saving Models to Disk...")
models = {
    'model_risk': model_risk,
    'model_score': model_score,
    'scaler': scaler,
    'encoders': {
        'gender': le_gender,
        'smoking': le_smoking,
        'activity': le_activity,
        'stress': le_stress,
        'mood': le_mood,
        'sleep_q': le_sleep_q,
        'balance': le_balance
    }
}

with open('healthcare_model.pkl', 'wb') as f:
    pickle.dump(models, f)

print("Workflow Complete. Model saved as 'healthcare_model.pkl'")
