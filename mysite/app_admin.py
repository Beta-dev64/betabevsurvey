from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, current_app
import os
import sqlite3
import csv
import io
import pandas as pd
import uuid
import functools
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Helper functions
def get_db_connection():
    conn = sqlite3.connect('dangote_execution.db')
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin dashboard
@admin_bp.route('/')
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get counts for dashboard
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM outlets")
    outlet_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM executions")
    execution_count = c.fetchone()[0]
    
    # Get recent activity
    c.execute("""
    SELECT e.id, e.execution_date, u.full_name as agent, o.outlet_name, o.region
    FROM executions e
    JOIN users u ON e.agent_id = u.id
    JOIN outlets o ON e.outlet_id = o.id
    ORDER BY e.execution_date DESC
    LIMIT 5
    """)
    recent_activity = c.fetchall()
    
    conn.close()
    
    return render_template('admin/dashboard.html', 
                           user_count=user_count, 
                           outlet_count=outlet_count, 
                           execution_count=execution_count,
                           recent_activity=recent_activity)

# User management
@admin_bp.route('/users')
@admin_required
def user_list():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all users
    c.execute("SELECT * FROM users ORDER BY username")
    users = c.fetchall()
    
    conn.close()
    
    return render_template('admin/user_list.html', users=users)

@admin_bp.route('/users/new', methods=['GET', 'POST'])
@admin_required
def user_new():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        region = request.form.get('region')
        state = request.form.get('state')
        lga = request.form.get('lga')
        
        # Validate input
        if not username or not password or not full_name or not role:
            flash('All fields are required', 'danger')
            return render_template('admin/user_form.html')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if username already exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            flash('Username already exists', 'danger')
            conn.close()
            return render_template('admin/user_form.html')
        
        # Insert new user
        c.execute('''
        INSERT INTO users (username, password, full_name, role, region, state, lga)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password, full_name, role, region, state, lga))
        
        conn.commit()
        conn.close()
        
        flash('User created successfully', 'success')
        return redirect(url_for('admin.user_list'))
    
    return render_template('admin/user_form.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def user_edit(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        # Don't allow editing the admin user
        if user_id == session['user_id'] and session['role'] == 'admin':
            if request.form.get('role') != 'admin':
                flash('Cannot change your own admin role', 'danger')
                return redirect(url_for('admin.user_list'))
        
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        role = request.form.get('role')
        region = request.form.get('region')
        state = request.form.get('state')
        lga = request.form.get('lga')
        
        # Update user details
        if password:  # Only update password if provided
            c.execute('''
            UPDATE users SET password = ?, full_name = ?, role = ?, region = ?, state = ?, lga = ?
            WHERE id = ?
            ''', (password, full_name, role, region, state, lga, user_id))
        else:
            c.execute('''
            UPDATE users SET full_name = ?, role = ?, region = ?, state = ?, lga = ?
            WHERE id = ?
            ''', (full_name, role, region, state, lga, user_id))
        
        conn.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.user_list'))
    
    # Get user details for editing
    c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.user_list'))
    
    conn.close()
    
    return render_template('admin/user_form.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def user_delete(user_id):
    # Don't allow deleting self
    if user_id == session['user_id']:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('admin.user_list'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if user has executions
    c.execute("SELECT COUNT(*) FROM executions WHERE agent_id = ?", (user_id,))
    execution_count = c.fetchone()[0]
    
    if execution_count > 0:
        flash(f'Cannot delete user with {execution_count} executions', 'danger')
        conn.close()
        return redirect(url_for('admin.user_list'))
    
    # Delete user
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.user_list'))

@admin_bp.route('/users/import', methods=['GET', 'POST'])
@admin_required
def user_import():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'danger')
            return redirect(request.url)
        
        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_data = csv.reader(stream)
            
            # Skip header
            header = next(csv_data)
            
            # Validate header
            required_fields = ['username', 'password', 'full_name', 'role', 'region']
            if not all(field in header for field in required_fields):
                flash(f'CSV file must contain: {", ".join(required_fields)}', 'danger')
                return redirect(request.url)
            
            # Get field indices
            username_idx = header.index('username')
            password_idx = header.index('password')
            full_name_idx = header.index('full_name')
            role_idx = header.index('role')
            region_idx = header.index('region')
            
            # Optional fields
            state_idx = header.index('state') if 'state' in header else -1
            lga_idx = header.index('lga') if 'lga' in header else -1
            
            conn = get_db_connection()
            c = conn.cursor()
            
            success_count = 0
            error_count = 0
            
            for row in csv_data:
                if len(row) < 5:  # Skip incomplete rows
                    continue
                
                username = row[username_idx].strip()
                password = row[password_idx].strip()
                full_name = row[full_name_idx].strip()
                role = row[role_idx].strip()
                region = row[region_idx].strip()
                
                # Optional fields
                state = row[state_idx].strip() if state_idx >= 0 and state_idx < len(row) else ''
                lga = row[lga_idx].strip() if lga_idx >= 0 and lga_idx < len(row) else ''
                
                # Validate role
                if role not in ['admin', 'field_agent']:
                    error_count += 1
                    continue
                
                # Check if username exists
                c.execute("SELECT id FROM users WHERE username = ?", (username,))
                if c.fetchone():
                    error_count += 1
                    continue
                
                # Insert user
                try:
                    c.execute('''
                    INSERT INTO users (username, password, full_name, role, region, state, lga)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (username, password, full_name, role, region, state, lga))
                    success_count += 1
                except Exception as e:
                    print(f"Error inserting user: {str(e)}")
                    error_count += 1
            
            conn.commit()
            conn.close()
            
            flash(f'Imported {success_count} users successfully, {error_count} errors', 'success')
            return redirect(url_for('admin.user_list'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            return redirect(request.url)
    
    return render_template('admin/user_import.html')

# Bulk User Operations
@admin_bp.route('/users/bulk_manage')
@admin_required
def user_bulk_manage():
    return render_template('admin/user_bulk_manage.html')

@admin_bp.route('/users/preview')
@admin_required
def user_preview():
    delete_by = request.args.get('delete_by')
    value = request.args.get('value')
    
    if not delete_by or not value:
        return jsonify({'users': []})
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Build query based on filter
    query = '''
    SELECT u.*, COUNT(e.id) as executions 
    FROM users u 
    LEFT JOIN executions e ON u.id = e.agent_id
    '''
    
    params = []
    
    if delete_by == 'region':
        query += " WHERE u.region = ?"
        params.append(value)
    elif delete_by == 'state':
        query += " WHERE u.state = ?"
        params.append(value)
    elif delete_by == 'lga':
        query += " WHERE u.lga = ?"
        params.append(value)
    
    query += " GROUP BY u.id"
    
    c.execute(query, params)
    users = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({'users': users})

@admin_bp.route('/users/bulk_delete', methods=['POST'])
@admin_required
def user_bulk_delete():
    delete_by = request.form.get('delete_by')
    
    # Get value based on delete_by
    if delete_by == 'region':
        value = request.form.get('region')
    elif delete_by == 'state':
        value = request.form.get('state')
    elif delete_by == 'lga':
        value = request.form.get('lga')
    else:
        flash('Invalid criteria', 'danger')
        return redirect(url_for('admin.user_bulk_manage'))
    
    if not value:
        flash('No value specified', 'danger')
        return redirect(url_for('admin.user_bulk_manage'))
    
    # Options
    skip_with_executions = 'skip_with_executions' in request.form
    skip_admins = 'skip_admins' in request.form
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Find users to delete
    query = f"SELECT id FROM users WHERE {delete_by} = ?"
    
    # Additional conditions
    if skip_with_executions:
        query += " AND id NOT IN (SELECT DISTINCT agent_id FROM executions)"
    
    if skip_admins:
        query += " AND role != 'admin'"
    
    # Don't delete current user
    query += f" AND id != {session['user_id']}"
    
    c.execute(query, (value,))
    user_ids = [row[0] for row in c.fetchall()]
    
    if not user_ids:
        flash('No users found matching the criteria or all users have executions/are admins', 'warning')
        conn.close()
        return redirect(url_for('admin.user_bulk_manage'))
    
    # Delete the users
    c.execute(f"DELETE FROM users WHERE id IN ({','.join(['?'] * len(user_ids))})", user_ids)
    
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    
    flash(f'Successfully deleted {deleted_count} users', 'success')
    return redirect(url_for('admin.user_list'))

# Outlet management
@admin_bp.route('/outlets')
@admin_required
def outlet_list():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all outlets
    c.execute("SELECT * FROM outlets ORDER BY region, state, local_govt, outlet_name")
    outlets = c.fetchall()
    
    conn.close()
    
    return render_template('admin/outlet_list.html', outlets=outlets)

@admin_bp.route('/outlets/new', methods=['GET', 'POST'])
@admin_required
def outlet_new():
    if request.method == 'POST':
        urn = request.form.get('urn')
        outlet_name = request.form.get('outlet_name')
        customer_name = request.form.get('customer_name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        outlet_type = request.form.get('outlet_type')
        local_govt = request.form.get('local_govt')
        state = request.form.get('state')
        region = request.form.get('region')
        
        # Validate input
        if not urn or not outlet_name or not region:
            flash('URN, Outlet Name and Region are required', 'danger')
            return render_template('admin/outlet_form.html')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if URN already exists
        c.execute("SELECT id FROM outlets WHERE urn = ?", (urn,))
        if c.fetchone():
            flash('URN already exists', 'danger')
            conn.close()
            return render_template('admin/outlet_form.html')
        
        # Insert new outlet
        c.execute('''
        INSERT INTO outlets (urn, outlet_name, customer_name, address, phone, outlet_type, local_govt, state, region)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (urn, outlet_name, customer_name, address, phone, outlet_type, local_govt, state, region))
        
        conn.commit()
        conn.close()
        
        flash('Outlet created successfully', 'success')
        return redirect(url_for('admin.outlet_list'))
    
    return render_template('admin/outlet_form.html')

@admin_bp.route('/outlets/edit/<int:outlet_id>', methods=['GET', 'POST'])
@admin_required
def outlet_edit(outlet_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    if request.method == 'POST':
        urn = request.form.get('urn')
        outlet_name = request.form.get('outlet_name')
        customer_name = request.form.get('customer_name')
        address = request.form.get('address')
        phone = request.form.get('phone')
        outlet_type = request.form.get('outlet_type')
        local_govt = request.form.get('local_govt')
        state = request.form.get('state')
        region = request.form.get('region')
        
        # Validate input
        if not urn or not outlet_name or not region:
            flash('URN, Outlet Name and Region are required', 'danger')
            c.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
            outlet = c.fetchone()
            conn.close()
            return render_template('admin/outlet_form.html', outlet=outlet)
        
        # Check if URN exists on another outlet
        c.execute("SELECT id FROM outlets WHERE urn = ? AND id != ?", (urn, outlet_id))
        if c.fetchone():
            flash('URN already exists on another outlet', 'danger')
            c.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
            outlet = c.fetchone()
            conn.close()
            return render_template('admin/outlet_form.html', outlet=outlet)
        
        # Update outlet
        c.execute('''
        UPDATE outlets 
        SET urn = ?, outlet_name = ?, customer_name = ?, address = ?, phone = ?, outlet_type = ?, 
        local_govt = ?, state = ?, region = ?
        WHERE id = ?
        ''', (urn, outlet_name, customer_name, address, phone, outlet_type, local_govt, state, region, outlet_id))
        
        conn.commit()
        flash('Outlet updated successfully', 'success')
        
        # Get updated outlet
        c.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
        outlet = c.fetchone()
        
        conn.close()
        return redirect(url_for('admin.outlet_list'))
    
    # Get outlet for editing
    c.execute("SELECT * FROM outlets WHERE id = ?", (outlet_id,))
    outlet = c.fetchone()
    
    if not outlet:
        flash('Outlet not found', 'danger')
        return redirect(url_for('admin.outlet_list'))
    
    conn.close()
    
    return render_template('admin/outlet_form.html', outlet=outlet)

@admin_bp.route('/outlets/delete/<int:outlet_id>', methods=['POST'])
@admin_required
def outlet_delete(outlet_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if outlet has executions
    c.execute("SELECT COUNT(*) FROM executions WHERE outlet_id = ?", (outlet_id,))
    execution_count = c.fetchone()[0]
    
    if execution_count > 0:
        flash(f'Cannot delete outlet with {execution_count} executions', 'danger')
        conn.close()
        return redirect(url_for('admin.outlet_list'))
    
    # Delete outlet
    c.execute("DELETE FROM outlets WHERE id = ?", (outlet_id,))
    conn.commit()
    conn.close()
    
    flash('Outlet deleted successfully', 'success')
    return redirect(url_for('admin.outlet_list'))

@admin_bp.route('/outlets/import', methods=['GET', 'POST'])
@admin_required
def outlet_import():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(request.url)
        
        if not file.filename.endswith('.csv'):
            flash('Please upload a CSV file', 'danger')
            return redirect(request.url)
        
        try:
            # Read CSV using pandas
            df = pd.read_csv(file)
            
            # Validate required columns
            required_columns = ['urn', 'outlet_name', 'region']
            if not all(col in df.columns for col in required_columns):
                flash(f'CSV must contain columns: {", ".join(required_columns)}', 'danger')
                return redirect(request.url)
            
            # Fill missing values with empty strings
            optional_columns = ['customer_name', 'address', 'phone', 'outlet_type', 'local_govt', 'state']
            for col in optional_columns:
                if col not in df.columns:
                    df[col] = ''
                else:
                    df[col] = df[col].fillna('')
            
            conn = get_db_connection()
            c = conn.cursor()
            
            success_count = 0
            update_count = 0
            error_count = 0
            
            # Process each row
            for _, row in df.iterrows():
                try:
                    # Check if outlet with URN exists
                    c.execute("SELECT id FROM outlets WHERE urn = ?", (row['urn'],))
                    existing = c.fetchone()
                    
                    if existing:
                        # Update existing outlet
                        c.execute('''
                        UPDATE outlets 
                        SET outlet_name = ?, customer_name = ?, address = ?, phone = ?, outlet_type = ?, 
                        local_govt = ?, state = ?, region = ?
                        WHERE urn = ?
                        ''', (
                            row['outlet_name'], row['customer_name'], row['address'], row['phone'], 
                            row['outlet_type'], row['local_govt'], row['state'], row['region'], row['urn']
                        ))
                        update_count += 1
                    else:
                        # Insert new outlet
                        c.execute('''
                        INSERT INTO outlets (urn, outlet_name, customer_name, address, phone, outlet_type, local_govt, state, region)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            row['urn'], row['outlet_name'], row['customer_name'], row['address'], row['phone'], 
                            row['outlet_type'], row['local_govt'], row['state'], row['region']
                        ))
                        success_count += 1
                
                except Exception as e:
                    print(f"Error processing row: {str(e)}")
                    error_count += 1
            
            conn.commit()
            conn.close()
            
            flash(f'Imported {success_count} new outlets, updated {update_count}, {error_count} errors', 'success')
            return redirect(url_for('admin.outlet_list'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            return redirect(request.url)
    
    # Provide a sample CSV template
    sample_data = [
        ['urn', 'outlet_name', 'customer_name', 'address', 'phone', 'outlet_type', 'local_govt', 'state', 'region'],
        ['DCP/22/SW/ED/1000009', 'SAMPLE OUTLET', 'JOHN DOE', '123 SAMPLE STREET', '08012345678', 'Shop', 'EGOR', 'EDO', 'SW']
    ]
    
    return render_template('admin/outlet_import.html', sample_data=sample_data)

# Bulk Outlet Operations
@admin_bp.route('/outlets/bulk_manage')
@admin_required
def outlet_bulk_manage():
    return render_template('admin/outlet_bulk_manage.html')

@admin_bp.route('/outlets/preview')
@admin_required
def outlet_preview():
    delete_by = request.args.get('delete_by')
    value = request.args.get('value')
    
    if not delete_by or not value:
        return jsonify({'outlets': []})
    
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Build query based on filter
    query = '''
    SELECT o.*, COUNT(e.id) as executions 
    FROM outlets o 
    LEFT JOIN executions e ON o.id = e.outlet_id
    '''
    
    params = []
    
    if delete_by == 'region':
        query += " WHERE o.region = ?"
        params.append(value)
    elif delete_by == 'state':
        query += " WHERE o.state = ?"
        params.append(value)
    elif delete_by == 'local_govt':
        query += " WHERE o.local_govt = ?"
        params.append(value)
    
    query += " GROUP BY o.id"
    
    c.execute(query, params)
    outlets = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({'outlets': outlets})

@admin_bp.route('/outlets/bulk_delete', methods=['POST'])
@admin_required
def outlet_bulk_delete():
    delete_by = request.form.get('delete_by')
    
    # Get value based on delete_by
    if delete_by == 'region':
        value = request.form.get('region')
    elif delete_by == 'state':
        value = request.form.get('state')
    elif delete_by == 'local_govt':
        value = request.form.get('local_govt')
    else:
        flash('Invalid criteria', 'danger')
        return redirect(url_for('admin.outlet_bulk_manage'))
    
    if not value:
        flash('No value specified', 'danger')
        return redirect(url_for('admin.outlet_bulk_manage'))
    
    # Options
    skip_with_executions = 'skip_with_executions' in request.form
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Find outlets to delete
    query = f"SELECT id FROM outlets WHERE {delete_by} = ?"
    
    # Additional conditions
    if skip_with_executions:
        query += " AND id NOT IN (SELECT DISTINCT outlet_id FROM executions)"
    
    c.execute(query, (value,))
    outlet_ids = [row[0] for row in c.fetchall()]
    
    if not outlet_ids:
        flash('No outlets found matching the criteria or all outlets have executions', 'warning')
        conn.close()
        return redirect(url_for('admin.outlet_bulk_manage'))
    
    # Delete the outlets
    c.execute(f"DELETE FROM outlets WHERE id IN ({','.join(['?'] * len(outlet_ids))})", outlet_ids)
    
    deleted_count = c.rowcount
    conn.commit()
    conn.close()
    
    flash(f'Successfully deleted {deleted_count} outlets', 'success')
    return redirect(url_for('admin.outlet_list'))

# Execution Management
@admin_bp.route('/executions')
@admin_required
def execution_list():
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
    SELECT e.id, e.execution_date, o.outlet_name, o.region, o.state, u.full_name as agent_name, e.status
    FROM executions e
    JOIN outlets o ON e.outlet_id = o.id
    JOIN users u ON e.agent_id = u.id
    ORDER BY e.execution_date DESC
    ''')
    
    executions = c.fetchall()
    conn.close()
    
    return render_template('admin/execution_list.html', executions=executions)

@admin_bp.route('/executions/delete/<int:execution_id>', methods=['POST'])
@admin_required
def execution_delete(execution_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get execution details to delete images
    c.execute("SELECT before_image, after_image FROM executions WHERE id = ?", (execution_id,))
    execution = c.fetchone()
    
    if execution:
        # Delete execution record
        c.execute("DELETE FROM executions WHERE id = ?", (execution_id,))
        conn.commit()
        
        # Delete associated images
        upload_folder = os.path.join(current_app.static_folder, 'uploads')
        
        if execution['before_image'] and os.path.exists(os.path.join(upload_folder, execution['before_image'])):
            try:
                os.remove(os.path.join(upload_folder, execution['before_image']))
            except:
                pass
        
        if execution['after_image'] and os.path.exists(os.path.join(upload_folder, execution['after_image'])):
            try:
                os.remove(os.path.join(upload_folder, execution['after_image']))
            except:
                pass
        
        flash('Execution deleted successfully', 'success')
    else:
        flash('Execution not found', 'danger')
    
    conn.close()
    return redirect(url_for('admin.execution_list'))