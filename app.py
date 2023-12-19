from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'hortalezaJose'  # Change this to a secure secret key

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'expense_tracker'

mysql = MySQL(app)

# Landing Page - Login
# Landing Page - Login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username:
            return render_template('login.html', error='Username is required.')
        elif not password:
            return render_template('login.html', error='Password is required.')
        else:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                # Assuming user ID is the first element in the tuple
                session['user_id'] = user[0]
                return redirect(url_for('home'))
            else:
                return render_template('login.html', error='Incorrect Username or Password.')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Add this function to fetch expenses from the database
def get_expenses(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
    expenses = cursor.fetchall()
    cursor.close()
    return expenses


# Home Page
@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    expenses = get_expenses(user_id)
    return render_template('home.html', expenses=expenses)

# Management Page
@app.route('/management')
def management():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    expenses = get_expenses(user_id)
    print(expenses) 
    return render_template('management.html', expenses=expenses)

# Add Expense
@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    try:
        title = request.form.get('title')
        amount = request.form.get('amount')

        if not title or not amount:
            return jsonify({'status': 'error', 'message': 'All fields are required'})

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO expenses (user_id,title, amount) VALUES (%s,%s, %s)", (user_id,title, amount))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'You have successfully added a new expense.'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
# Edit Expense
@app.route('/edit_expense/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        title = request.form.get('editTitle')
        amount = request.form.get('editAmount')

        if not title or not amount:
            return jsonify({'status': 'error', 'message': 'All fields are required'})

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE expenses SET title = %s, amount = %s WHERE id = %s AND user_id = %s",
                       (title, amount, expense_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Expense updated successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

#delete expense
@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = %s AND user_id = %s",
                       (expense_id, user_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({'status': 'success', 'message': 'Expense deleted successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
