from flask import Flask, render_template,request,redirect,url_for
import sqlite3
import random
from flask_login import LoginManager, login_user, logout_user, current_user

app = Flask(__name__)


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
login_manager = LoginManager()
login_manager.init_app(app)



def create_database():
    conn = sqlite3.connect('ipodetails.db')
    c = conn.cursor()
    
    # Create IPO details table
    c.execute('''CREATE TABLE IF NOT EXISTS ipo_details
                 (id INTEGER PRIMARY KEY, company_name TEXT, num_shares INTEGER, price_per_share REAL)''')
    
    # Create user data table
    c.execute('''CREATE TABLE IF NOT EXISTS user_data
                 (id INTEGER PRIMARY KEY, ipo_id INTEGER, friend_name TEXT, amount_invested REAL)''')
    
    conn.commit()
    conn.close()

# Call the function to create both tables when the Flask app starts
create_database()



def generate_id():
    conn = sqlite3.connect('ipodetails.db')
    c = conn.cursor()
    
    while True:
        id = random.randint(10000, 99999)
        c.execute("SELECT * FROM ipo_details WHERE id = ?", (id,))
        if not c.fetchone():  # Check if ID is not already in use
            break

    conn.close()
    return id


@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        company_name = request.form['company_name']
        num_shares = int(request.form['num_shares'])
        price_per_share = float(request.form['price_per_share'])

        # Generate a random ID
        id = generate_id()

        # Insert data into the database
        conn = sqlite3.connect('ipodetails.db')
        c = conn.cursor()
        c.execute("INSERT INTO ipo_details (id, company_name, num_shares, price_per_share) VALUES (?, ?, ?, ?)",
                  (id, company_name, num_shares, price_per_share))
        conn.commit()
        conn.close()

        return redirect(url_for('ipo'))

    return render_template('add.html')


@app.route('/apply/<int:ipo_id>')
def apply_form(ipo_id):
    conn = sqlite3.connect('ipodetails.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ipo_details WHERE id = ?", (ipo_id,))
    ipo_details = c.fetchone()
    conn.close()
    return render_template('apply.html', ipo_details=ipo_details)

@app.route('/apply', methods=['POST'])
def apply_submit():
    if request.method == 'POST':
        ipo_id = request.form['ipo_id']

        # Connect to database
        conn = sqlite3.connect('ipodetails.db')
        c = conn.cursor()

        # Generate unique ID
        unique_id = generate_id()

        # Insert user data into database
        for key, value in request.form.items():
            if key.startswith('friendName'):
                friend_num = key[10:]
                friend_name = value
                friend_amount = request.form.get(f'friendAmount{friend_num}', type=float)
                print(friend_amount,friend_name,friend_num)
                c.execute("INSERT INTO user_data (id, ipo_id, friend_name, amount_invested) VALUES (?, ?, ?, ?)",
                          (unique_id, ipo_id, friend_name, friend_amount))

        # Commit changes and close connection
        conn.commit()
        conn.close()

        return redirect(url_for('success', unique_id=unique_id))

@app.route('/success/<int:unique_id>')
def success(unique_id):
    return f"<h1>Success! Data added with ID: {unique_id}</h1>"






@app.route('/')
def index():
    return render_template('index.html')


@app.route('/ipo')
def ipo():
    # Fetch IPO data from the database
    conn = sqlite3.connect('ipodetails.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ipo_details")
    ipo_listings = c.fetchall()
    conn.close()
    return render_template('ipo.html', ipo_listings=ipo_listings)



if __name__ == '__main__':
    app.run(debug=True)
