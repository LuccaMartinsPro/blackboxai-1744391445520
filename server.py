from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_url_path='')
CORS(app)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Serve static files
@app.route('/')
def root():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Database initialization
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            profile_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Relationships table (PT-Student, Nutritionist-Student)
    c.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer_id INTEGER,
            student_id INTEGER,
            nutritionist_id INTEGER,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trainer_id) REFERENCES users (id),
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (nutritionist_id) REFERENCES users (id)
        )
    ''')
    
    # Workout plans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trainer_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (trainer_id) REFERENCES users (id),
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    # Exercises table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            sets INTEGER,
            reps INTEGER,
            video_url TEXT,
            day_of_week INTEGER,
            order_index INTEGER,
            FOREIGN KEY (plan_id) REFERENCES workout_plans (id)
        )
    ''')
    
    # Progress tracking table
    c.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            exercise_id INTEGER NOT NULL,
            completed BOOLEAN,
            feedback TEXT,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users (id),
            FOREIGN KEY (exercise_id) REFERENCES exercises (id)
        )
    ''')
    
    # Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            read BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Helper functions
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def user_exists(email):
    conn = get_db()
    user = conn.execute('SELECT 1 FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return bool(user)

# Authentication routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if user_exists(data['email']):
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (email, password, name, role, profile_data) VALUES (?, ?, ?, ?, ?)',
            (data['email'], hashed_password, data['name'], data['role'], data.get('profile_data'))
        )
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    conn = get_db()
    user = conn.execute(
        'SELECT * FROM users WHERE email = ?', (data['email'],)
    ).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], data['password']):
        session['user_id'] = user['id']
        return jsonify({
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        })
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'})

# User routes
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    user = conn.execute('SELECT id, email, name, role, profile_data FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    
    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    conn = get_db()
    try:
        conn.execute(
            'UPDATE users SET name = ?, profile_data = ? WHERE id = ?',
            (data['name'], data.get('profile_data'), user_id)
        )
        conn.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Workout plan routes
@app.route('/api/workout-plans', methods=['POST'])
def create_workout_plan():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    conn = get_db()
    
    try:
        # Verify trainer-student relationship
        relationship = conn.execute(
            'SELECT 1 FROM relationships WHERE trainer_id = ? AND student_id = ?',
            (session['user_id'], data['student_id'])
        ).fetchone()
        
        if not relationship:
            return jsonify({'error': 'Unauthorized: Not trainer for this student'}), 403
        
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO workout_plans 
               (trainer_id, student_id, name, description, start_date, end_date)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (session['user_id'], data['student_id'], data['name'],
             data.get('description'), data['start_date'], data['end_date'])
        )
        
        plan_id = cursor.lastrowid
        
        # Insert exercises
        for day in data['exercises']:
            for idx, exercise in enumerate(day['exercises']):
                cursor.execute(
                    '''INSERT INTO exercises 
                       (plan_id, name, description, sets, reps, video_url, day_of_week, order_index)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (plan_id, exercise['name'], exercise.get('description'),
                     exercise['sets'], exercise['reps'], exercise.get('video_url'),
                     day['day'], idx)
                )
        
        conn.commit()
        return jsonify({'message': 'Workout plan created successfully', 'plan_id': plan_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/workout-plans/<int:plan_id>', methods=['GET'])
def get_workout_plan(plan_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    plan = conn.execute(
        '''SELECT wp.*, u.name as trainer_name 
           FROM workout_plans wp
           JOIN users u ON wp.trainer_id = u.id
           WHERE wp.id = ? AND (wp.trainer_id = ? OR wp.student_id = ?)''',
        (plan_id, session['user_id'], session['user_id'])
    ).fetchone()
    
    if not plan:
        return jsonify({'error': 'Plan not found or unauthorized'}), 404
    
    exercises = conn.execute(
        'SELECT * FROM exercises WHERE plan_id = ? ORDER BY day_of_week, order_index',
        (plan_id,)
    ).fetchall()
    
    plan_dict = dict(plan)
    plan_dict['exercises'] = [dict(ex) for ex in exercises]
    
    conn.close()
    return jsonify(plan_dict)

# Progress tracking routes
@app.route('/api/progress', methods=['POST'])
def log_progress():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    conn = get_db()
    
    try:
        conn.execute(
            'INSERT INTO progress (student_id, exercise_id, completed, feedback) VALUES (?, ?, ?, ?)',
            (session['user_id'], data['exercise_id'], data['completed'], data.get('feedback'))
        )
        conn.commit()
        return jsonify({'message': 'Progress logged successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Messaging routes
@app.route('/api/messages', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    conn = get_db()
    
    try:
        conn.execute(
            'INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)',
            (session['user_id'], data['receiver_id'], data['content'])
        )
        conn.commit()
        return jsonify({'message': 'Message sent successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    conn = get_db()
    messages = conn.execute(
        '''SELECT m.*, u.name as sender_name 
           FROM messages m
           JOIN users u ON m.sender_id = u.id
           WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
           ORDER BY created_at DESC''',
        (session['user_id'], user_id, user_id, session['user_id'])
    ).fetchall()
    
    conn.close()
    return jsonify([dict(msg) for msg in messages])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
