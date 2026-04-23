import os
import json
import uuid
import hashlib
from functools import wraps
from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_library_key'

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ROLES_FILE = os.path.join(DATA_DIR, 'roles.json')

# Initialize data files if they don't exist
def init_db():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    if not os.path.exists(ROLES_FILE):
        roles = {
            "admin": ["manage_users", "manage_books", "borrow_books"],
            "librarian": ["manage_books", "borrow_books"],
            "student": ["borrow_books"]
        }
        with open(ROLES_FILE, 'w') as f:
            json.dump(roles, f, indent=4)
            
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f, indent=4)

def load_data(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password, salt=None):
    """
    Hashes a password using SHA-256 with a salt.
    Strengths: Salt prevents rainbow table attacks. Deterministic for same salt.
    Weaknesses: SHA-256 is fast, so vulnerable to brute force if salt is known.
    """
    if salt is None:
        salt = uuid.uuid4().hex
    
    # Encode password and salt
    salted_password = password.encode('utf-8') + salt.encode('utf-8')
    password_hash = hashlib.sha256(salted_password).hexdigest()
    
    return password_hash, salt

# Decorator for RBAC Authorization
def require_permission(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in to access this page.", "danger")
                return redirect(url_for('login'))
            
            users = load_data(USERS_FILE)
            user = users.get(session['user_id'])
            if not user:
                session.clear()
                return redirect(url_for('login'))
                
            roles = load_data(ROLES_FILE)
            user_roles = user.get('roles', [])
            
            # Check if any of the user's roles have the required permission
            has_permission = False
            for role in user_roles:
                if permission in roles.get(role, []):
                    has_permission = True
                    break
                    
            if not has_permission:
                flash(f"Unauthorized. You need '{permission}' permission.", "danger")
                return redirect(url_for('dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_data(USERS_FILE)
        
        # Find user
        user_id = None
        user_data = None
        for uid, udata in users.items():
            if udata['username'] == username:
                user_id = uid
                user_data = udata
                break
                
        if user_data:
            # Check password
            salt = user_data['salt']
            stored_hash = user_data['password_hash']
            calc_hash, _ = hash_password(password, salt)
            
            if calc_hash == stored_hash:
                if not user_data.get('approved', False):
                    flash("Your account is pending approval by an admin.", "warning")
                    return render_template('login.html')
                    
                session['user_id'] = user_id
                session['username'] = username
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password.", "danger")
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        users = load_data(USERS_FILE)
        
        # Check if username exists
        for uid, udata in users.items():
            if udata['username'] == username:
                flash("Username already exists.", "danger")
                return render_template('register.html')
        
        # Provision user
        user_id = str(uuid.uuid4())
        password_hash, salt = hash_password(password)
        
        # Determine if approval is needed (e.g. admins/librarians need approval, students auto-approved)
        approved = True if role == 'student' else False
        
        # In a real system, first user might automatically be admin, or created via CLI.
        # For simplicity, if no admin exists, make the first admin approved automatically.
        has_admin = any('admin' in u['roles'] for u in users.values())
        if not has_admin and role == 'admin':
            approved = True

        users[user_id] = {
            "username": username,
            "password_hash": password_hash,
            "salt": salt,
            "roles": [role],
            "approved": approved
        }
        
        save_data(USERS_FILE, users)
        
        if approved:
            flash("Registration successful. You can now log in.", "success")
        else:
            flash("Registration successful. Please wait for an admin to approve your account.", "info")
            
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    users = load_data(USERS_FILE)
    user = users.get(session['user_id'])
    
    return render_template('dashboard.html', user=user)

@app.route('/admin/users')
@require_permission('manage_users')
def manage_users():
    users = load_data(USERS_FILE)
    return render_template('admin.html', users=users)

@app.route('/admin/approve/<user_id>')
@require_permission('manage_users')
def approve_user(user_id):
    users = load_data(USERS_FILE)
    if user_id in users:
        users[user_id]['approved'] = True
        save_data(USERS_FILE, users)
        flash(f"User {users[user_id]['username']} approved.", "success")
    return redirect(url_for('manage_users'))

@app.route('/admin/delete/<user_id>')
@require_permission('manage_users')
def delete_user(user_id):
    users = load_data(USERS_FILE)
    if user_id in users:
        username = users[user_id]['username']
        del users[user_id]
        save_data(USERS_FILE, users)
        flash(f"User {username} deleted.", "success")
    return redirect(url_for('manage_users'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
