from flask import Flask, request, render_template, redirect, url_for, session
import math
import re  # Regex for email & password validation
import sqlite3
import pickle

model = None  # Default None rakho

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
        print("✅ Model Loaded Successfully")  # Debugging ke liye
except FileNotFoundError:
    print("⚠️ model.pkl file not found! Running in demo mode.")
except Exception as e:
    print(f"⚠️ Error loading model: {e}")

def predict_result(year, city_code, pop, crime_code):
    if model:
        return model.predict([[year, city_code, pop, crime_code]])[0]
    
    # Fake result agar model nahi mila toh
    return (int(year) % 10) + (int(city_code) % 5) + (int(pop) % 3) + (int(crime_code) % 7)

app = Flask(__name__)
app.secret_key = "supersecretkey"

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)''')
    conn.commit()
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(email_pattern, email):
            error = "Only Gmail accounts are allowed!"
            return render_template("login.html", error=error)

        password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_pattern, password):
            error = "Weak password! Use at least 8 chars, 1 uppercase, 1 number & 1 special char."
            return render_template("login.html", error=error)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = email
            return redirect(url_for('about'))
        else:
            error = "Invalid credentials or user not registered!"

    return render_template("login.html", error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        email_pattern = r'^[a-zA-Z0-9._%+-]+@gmail\.com$'
        if not re.match(email_pattern, email):
            error = "Only Gmail accounts are allowed!"
            return render_template("register.html", error=error)

        password_pattern = r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
        if not re.match(password_pattern, password):
            error = "Weak password! Use at least 8 chars, 1 uppercase, 1 number & 1 special char."
            return render_template("register.html", error=error)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            error = "Email already registered!"

    return render_template("register.html", error=error)

@app.route('/about')
def about():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("about.html")

@app.route('/index') 
def index(): 
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    city_names = {'0': 'Ahmedabad', '1': 'Bengaluru', '2': 'Chennai', '3': 'Coimbatore', '4': 'Delhi',
                  '5': 'Ghaziabad', '6': 'Hyderabad', '7': 'Indore', '8': 'Jaipur', '9': 'Kanpur',
                  '10': 'Kochi', '11': 'Kolkata', '12': 'Kozhikode', '13': 'Lucknow', '14': 'Mumbai',
                  '15': 'Nagpur', '16': 'Patna', '17': 'Pune', '18': 'Surat'}
    
    crimes_names = {'0': 'Crime Committed by Juveniles', '1': 'Crime against SC', '2': 'Crime against ST',
                    '3': 'Crime against Senior Citizen', '4': 'Crime against children', '5': 'Crime against women',
                    '6': 'Cyber Crimes', '7': 'Economic Offences', '8': 'Kidnapping', '9': 'Murder'}
    
    population = {'0': 63.50, '1': 85.00, '2': 87.00, '3': 21.50, '4': 163.10, '5': 23.60, '6': 77.50, '7': 21.70,
                  '8': 30.70, '9': 29.20, '10': 21.20, '11': 141.10, '12': 20.30, '13': 29.00, '14': 184.10, '15': 25.00,
                  '16': 20.50, '17': 50.50, '18': 45.80}

    city_code = request.form["city"]
    crime_code = request.form['crime']
    year = request.form['year']
    pop = population[city_code]

    year_diff = int(year) - 2011
    pop = abs(pop * (1 + 0.01 * year_diff))    

    crime_rate = predict_result(year, city_code, pop, crime_code)
    city_name = city_names[city_code]
    crime_type = crimes_names[crime_code]

    if crime_rate <= 1:
        crime_status = "Very Low Crime Area"
    elif crime_rate <= 5:
        crime_status = "Low Crime Area"
    elif crime_rate <= 15:
        crime_status = "High Crime Area"
    else:
        crime_status = "Very High Crime Area"

    cases = abs(math.ceil(crime_rate * pop))

    return render_template('result.html', city_name=city_name, crime_type=crime_type, year=year,
                           crime_status=crime_status, crime_rate=crime_rate, cases=cases, population=pop)

if __name__ == '__main__':
    app.run(debug=True)
