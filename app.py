from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import re
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )

def is_valid_college_email(email):
    return email.endswith('kongu.edu')

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get search and category filters
    search = request.args.get('search', '')
    category = request.args.get('category', '')

    query = """
        SELECT l.*, u.name as seller_name, u.email as seller_email 
        FROM listings l 
        JOIN users u ON l.seller_id = u.id 
        WHERE l.status = 'Available'
    """
    params = []

    if search:
        query += " AND (l.title LIKE %s OR l.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    if category:
        query += " AND l.category = %s"
        params.append(category)

    query += " ORDER BY l.id DESC"

    cursor.execute(query, params)
    listings = cursor.fetchall()

    # Get categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM listings WHERE status = 'Available'")
    categories = [row['category'] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return render_template('index.html', listings=listings, categories=categories, 
                         search=search, selected_category=category)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        college_name = request.form['college_name']

        if not is_valid_college_email(email):
            flash('Please use a valid college email ending with kongu.edu', 'error')
            return render_template('signup.html')

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered', 'error')
            cursor.close()
            conn.close()
            return render_template('signup.html')

        # Insert new user
        hashed_password = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO users (name, email, password, college_name, verified) 
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, hashed_password, college_name, True))  # Auto-verify for demo

        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Login successful!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
            cursor.close()
            conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/add_listing', methods=['GET', 'POST'])
def add_listing():
    if 'user_id' not in session:
        flash('Please login to add a listing', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = float(request.form['price'])
        category = request.form['category']

        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_path = filename

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO listings (title, description, price, category, image_path, seller_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, price, category, image_path, session['user_id']))

        conn.commit()
        cursor.close()
        conn.close()

        flash('Listing added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_listing.html')

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT l.*, u.name as seller_name, u.email as seller_email 
        FROM listings l 
        JOIN users u ON l.seller_id = u.id 
        WHERE l.id = %s
    """, (listing_id,))

    listing = cursor.fetchone()

    if not listing:
        flash('Listing not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    # Get seller's average rating
    cursor.execute("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as rating_count 
        FROM ratings WHERE seller_id = %s
    """, (listing['seller_id'],))

    rating_data = cursor.fetchone()
    avg_rating = rating_data['avg_rating'] if rating_data['avg_rating'] else 0
    rating_count = rating_data['rating_count']

    cursor.close()
    conn.close()

    return render_template('listing_detail.html', listing=listing, 
                         avg_rating=round(avg_rating, 1), rating_count=rating_count)

@app.route('/chats')
def chats():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user_id = session['user_id']

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Get latest message per conversation
    cur.execute("""
        SELECT u.id AS sender_id,
               u.name AS sender_name,
               m.message_text,
               m.timestamp
        FROM (
            SELECT 
                CASE 
                    WHEN sender_id = %s THEN receiver_id
                    ELSE sender_id
                END AS other_user_id,
                message_text,
                timestamp
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
        ) m
        JOIN users u ON u.id = m.other_user_id
        JOIN (
            -- get latest timestamp per conversation
            SELECT 
                CASE 
                    WHEN sender_id = %s THEN receiver_id
                    ELSE sender_id
                END AS other_user_id,
                MAX(timestamp) AS latest_time
            FROM messages
            WHERE sender_id = %s OR receiver_id = %s
            GROUP BY other_user_id
        ) latest ON latest.other_user_id = m.other_user_id AND latest.latest_time = m.timestamp
        ORDER BY m.timestamp DESC
    """, (current_user_id, current_user_id, current_user_id,
          current_user_id, current_user_id, current_user_id))

    senders = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('message.html', senders=senders)



@app.route('/messages/<int:other_user_id>')
def messages(other_user_id):
    if 'user_id' not in session:
        flash('Please login to access messages', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get other user info
    cursor.execute("SELECT name, email FROM users WHERE id = %s", (other_user_id,))
    other_user = cursor.fetchone()

    if not other_user:
        flash('User not found', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    # Get messages between current user and other user
    cursor.execute("""
        SELECT m.*, u.name as sender_name 
        FROM messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE (m.sender_id = %s AND m.receiver_id = %s) 
           OR (m.sender_id = %s AND m.receiver_id = %s)
        ORDER BY m.timestamp ASC
    """, (session['user_id'], other_user_id, other_user_id, session['user_id']))

    messages_list = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('chat.html', messages=messages_list, 
                         other_user=other_user, other_user_id=other_user_id)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'})

    receiver_id = request.form['receiver_id']
    message_text = request.form['message_text']
    listing_id = request.form.get('listing_id', None)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, listing_id, message_text) 
        VALUES (%s, %s, %s, %s)
    """, (session['user_id'], receiver_id, listing_id, message_text))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})

@app.route('/mark_sold/<int:listing_id>')
def mark_sold(listing_id):
    if 'user_id' not in session:
        flash('Please login', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify user owns this listing
    cursor.execute("SELECT seller_id FROM listings WHERE id = %s", (listing_id,))
    result = cursor.fetchone()

    if not result or result[0] != session['user_id']:
        flash('You can only mark your own listings as sold', 'error')
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    # Update listing status
    cursor.execute("UPDATE listings SET status = 'Sold' WHERE id = %s", (listing_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Listing marked as sold!', 'success')
    return redirect(url_for('profile'))

@app.route('/rate/<int:seller_id>', methods=['GET', 'POST'])
def rate_seller(seller_id):
    if 'user_id' not in session:
        flash('Please login to leave a rating', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        rating = int(request.form['rating'])
        review_text = request.form['review_text']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if user already rated this seller
        cursor.execute("""
            SELECT id FROM ratings 
            WHERE reviewer_id = %s AND seller_id = %s
        """, (session['user_id'], seller_id))

        if cursor.fetchone():
            flash('You have already rated this seller', 'error')
        else:
            cursor.execute("""
                INSERT INTO ratings (reviewer_id, seller_id, rating, review_text) 
                VALUES (%s, %s, %s, %s)
            """, (session['user_id'], seller_id, rating, review_text))
            conn.commit()
            flash('Rating submitted successfully!', 'success')

        cursor.close()
        conn.close()
        return redirect(url_for('profile'))

    # GET request - show rating form
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT name FROM users WHERE id = %s", (seller_id,))
    seller = cursor.fetchone()
    cursor.close()
    conn.close()

    if not seller:
        flash('Seller not found', 'error')
        return redirect(url_for('index'))

    return render_template('rate_seller.html', seller=seller, seller_id=seller_id)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Please login to access profile', 'error')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get user's listings
    cursor.execute("""
        SELECT * FROM listings WHERE seller_id = %s ORDER BY id DESC
    """, (session['user_id'],))
    user_listings = cursor.fetchall()

    # Get user's average rating
    cursor.execute("""
        SELECT AVG(rating) as avg_rating, COUNT(*) as rating_count 
        FROM ratings WHERE seller_id = %s
    """, (session['user_id'],))

    rating_data = cursor.fetchone()
    avg_rating = rating_data['avg_rating'] if rating_data['avg_rating'] else 0
    rating_count = rating_data['rating_count']

    # Get recent ratings received
    cursor.execute("""
        SELECT r.*, u.name as reviewer_name 
        FROM ratings r 
        JOIN users u ON r.reviewer_id = u.id 
        WHERE r.seller_id = %s 
        ORDER BY r.id DESC LIMIT 5
    """, (session['user_id'],))
    recent_ratings = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('profile.html', listings=user_listings, 
                         avg_rating=round(avg_rating, 1), rating_count=rating_count,
                         recent_ratings=recent_ratings)

if __name__ == '__main__':
    app.run(debug=True)
