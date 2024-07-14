from flask import Flask, flash,get_flashed_messages, render_template, request, redirect, url_for, session
import mysql.connector
import re
import os
from datetime import datetime, timedelta
import pandas as pd
import secrets
import string

def generate_secret_key(length=24):
    alphabet = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app = Flask(__name__)
app.secret_key = generate_secret_key()

# MySQL Connection

#db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="root",
#    database="library_management"
#)

db = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', 'root'),
    database=os.getenv('DB_NAME', 'library_management')
)

# Function to calculate due date excluding weekends
def calculate_due_date(start_date):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = start_date + pd.offsets.CustomBusinessDay(n=30)
    return end_date.strftime('%Y-%m-%d')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Validate password format
        if not re.match(r'^[A-Za-z0-9@#$%^&+=]{4,8}$', password):
            return "Invalid password format. It should be 4-8 characters."
        
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['username'] = username
            return redirect(url_for('book_management'))
        else:
            return "Login failed. Invalid username or password."
    
    return render_template('login.html')


@app.route('/book_management', methods=['GET', 'POST'])
def book_management():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT category FROM books")
    categories = cursor.fetchall()

    books_by_category = {}
    for category in categories:
        cursor.execute("SELECT * FROM books WHERE category = %s", (category['category'],))
        books_by_category[category['category']] = cursor.fetchall()
    
    # Fetch books already in the cart
    cursor.execute("SELECT book_id FROM cart WHERE username=%s", (session['username'],))
    cart_books = {row['book_id'] for row in cursor.fetchall()}  # Changed this line to use dictionary key
    
    cursor.close()

    if request.method == 'POST':
        selected_books = request.form.getlist('book_id')
        
        if not selected_books:
            flash("Please choose at least one book.", 'error')
            return redirect(url_for('book_management'))

        cursor = db.cursor()
        try:
            for book_id in selected_books:
                # Check if the book is already in the cart
                cursor.execute("SELECT title FROM books WHERE id = %s", (book_id,))
                book_title = cursor.fetchone()[0]

                cursor.execute("SELECT * FROM cart WHERE username=%s AND book_id=%s", (session['username'], book_id))
                existing_book = cursor.fetchone()
                if existing_book:
                    flash(f"Book '{book_title}' is already in your cart.", 'error')
                    continue
                
                # Calculate due date
                start_date = datetime.now().strftime('%Y-%m-%d')
                due_date = calculate_due_date(start_date)
                
                # Add book to cart
                cursor.execute("INSERT INTO cart (username, book_id, start_date, due_date) VALUES (%s, %s, %s, %s)",
                               (session['username'], book_id, start_date, due_date))
                db.commit()
                
                # Flash success message for each book added
                flash(f"Book '{book_title}' added to your cart successfully.", 'success')
                
            return redirect(url_for('view_cart'))

        except Exception as e:
            flash(f"Error adding book to cart: {str(e)}", 'error')

        finally:
            cursor.close()

    return render_template('book_management.html', books_by_category=books_by_category, cart_books=cart_books)






# Route to view cart contents
@app.route('/cart')
def view_cart():
    username = session.get('username')  # Assuming you store username in session after login

    cursor = db.cursor(dictionary=True)
    try:
        # Fetch cart items for the user
        cursor.execute("SELECT b.title, b.category, c.start_date, c.due_date FROM cart c INNER JOIN books b ON c.book_id = b.id WHERE c.username = %s", (username,))
        cart_items = cursor.fetchall()

        # Fetch flashed messages
        messages = get_flashed_messages(with_categories=True)

        # Extract titles from success messages
        book_titles = []
        for category, message in messages:
            if category == 'success':
                # Extract book title from the message
                match = re.search(r"Book '(.+?)' added to your cart successfully\.", message)
                if match:
                    book_titles.append(match.group(1))

        return render_template('cart.html', cart_items=cart_items, book_titles=book_titles)

    except Exception as e:
        flash(f"Error fetching cart items: {str(e)}", 'error')

    finally:
        cursor.close()

    return "Error fetching cart items"


@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the user from the session
    #flash('You have been logged out.', 'info')  # Flash a message
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
