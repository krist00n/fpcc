from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify, make_response
import mysql.connector
from datetime import datetime
import csv
import io


app = Flask(__name__)

# Konfigurasi database
db = mysql.connector.connect(
    host="localhost",
    user="root",  # Ganti dengan username MySQL Anda
    password="",  # Ganti dengan password MySQL Anda
    database="fprentalps"  # Ganti dengan nama database Anda
)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Route untuk halaman home
@app.route('/')
def home():
    if 'username' in session:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device")
        devices = cursor.fetchall()
        return render_template('home.html', devices=devices)
    else:
        return redirect(url_for('login'))

# Route untuk halaman login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = db.cursor()
        # Query untuk mencari user berdasarkan username dan password
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        
        if user:
            session['username'] = username
            session['user_id'] = user[0]
            session['role'] = user[6]  # Mengambil role dari user
            
            flash('Login berhasil!', 'success')
            if user[6] == 'admin':
                return redirect(url_for('admin_home'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Username atau password salah', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form['nama']
        username = request.form['username']
        no_hp = request.form.get('no_hp', '')  # Memastikan no_hp diambil dari form
        alamat = request.form['alamat']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        
        if password != confirm_password:
            flash('Konfirmasi password tidak sesuai', 'error')
            return redirect(request.url)
        
        cursor = db.cursor()
        # Cek apakah username sudah digunakan
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user:
            flash('Username sudah digunakan', 'error')
            return redirect(request.url)
        else:
            # Insert user baru ke database dengan role member
            cursor.execute("INSERT INTO users (username, password, nama, no_hp, alamat, role) VALUES (%s, %s, %s, %s, %s, %s)", (username, password, nama, no_hp, alamat, 'member'))
            db.commit()
            flash('Registrasi berhasil! Silakan login.', 'success')
            return redirect(url_for('login'))
    
    return render_template('regis.html')

# Route untuk logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Anda telah berhasil logout', 'info')
    return redirect(url_for('login'))

# Route untuk halaman pembayaran
@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        device_id = request.form['device']
        rental_date = request.form['rental-date']
        return_date = request.form['return-date']
        user_id = session.get('user_id')
        
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device WHERE id_device = %s", (device_id,))
        device = cursor.fetchone()
        
        if device:
            rental_date_obj = datetime.strptime(rental_date, "%Y-%m-%d")
            return_date_obj = datetime.strptime(return_date, "%Y-%m-%d")
            days_rented = (return_date_obj - rental_date_obj).days
            total_amount = days_rented * device['harga']
            
            insert_query = """
            INSERT INTO sewa (tanggal_sewa, tanggal_kembali, total_harga, device_id, user_id) 
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (rental_date, return_date, total_amount, device_id, user_id))
            db.commit()
            
            flash('Pembayaran berhasil diproses!', 'success')
            # Redirect ke halaman cetak nota
            return redirect(url_for('print_nota', rental_date=rental_date, return_date=return_date, device_name=device['device'], total_amount=total_amount))
    
    # Mengambil daftar perangkat untuk dropdown
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM device")
    devices = cursor.fetchall()
    
    return render_template('payment.html', devices=devices)

# Route untuk halaman cetak nota
@app.route('/print_nota')
def print_nota():
    rental_date = request.args.get('rental_date')
    return_date = request.args.get('return_date')
    device_name = request.args.get('device_name')
    total_amount = request.args.get('total_amount')
    member_name = session.get('username')
    
    return render_template('nota.html', rental_date=rental_date, return_date=return_date, device_name=device_name, total_amount=total_amount, member_name=member_name)

# Route untuk mengambil harga perangkat dengan AJAX
@app.route('/get_device_price/<int:device_id>')
def get_device_price(device_id):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT harga FROM device WHERE id_device = %s", (device_id,))
    device = cursor.fetchone()
    
    if device:
        return jsonify(device)
    else:
        return jsonify({'error': 'Device not found'}), 404
    
# Route untuk halaman admin home
@app.route('/admin')
def admin_home():
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor(dictionary=True)
        
        # Query untuk total users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        # Query untuk total products
        cursor.execute("SELECT COUNT(*) AS total_products FROM device")
        total_products = cursor.fetchone()['total_products']
        
        # Query untuk total orders
        cursor.execute("SELECT COUNT(*) AS total_orders FROM sewa")
        total_orders = cursor.fetchone()['total_orders']
        
        # Query untuk users
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        # Query untuk products
        cursor.execute("SELECT * FROM device")
        products = cursor.fetchall()
        
        # Query untuk orders
        cursor.execute("SELECT sewa.id_sewa, users.username, users.no_hp, device.device, sewa.tanggal_kembali FROM sewa JOIN users ON sewa.user_id = users.id JOIN device ON sewa.device_id = device.id_device")
        orders = cursor.fetchall()
        
        return render_template('admin_home.html', total_users=total_users, total_products=total_products, total_orders=total_orders, users=users, products=products, orders=orders)
    else:
        flash('Anda tidak memiliki akses sebagai admin', 'error')
        return redirect(url_for('login'))

# Route untuk menghapus user
@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor()
        # Query untuk menghapus user berdasarkan user_id
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        flash(f'User dengan ID {user_id} berhasil dihapus', 'success')
    return redirect(url_for('admin_home'))

# Route untuk menghapus produk
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor()
        # Query untuk menghapus produk berdasarkan product_id
        cursor.execute("DELETE FROM device WHERE id_device = %s", (product_id,))
        db.commit()
        flash(f'Produk dengan ID {product_id} berhasil dihapus', 'success')
    return redirect(url_for('admin_home'))

# Route untuk menghapus order
@app.route('/admin/delete_order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor()
        # Query untuk menghapus order berdasarkan order_id
        cursor.execute("DELETE FROM sewa WHERE id_sewa = %s", (order_id,))
        db.commit()
        flash(f'Order dengan ID {order_id} berhasil dihapus', 'success')
    return redirect(url_for('admin_home'))

# Route untuk edit user
@app.route('/admin/edit_user/<int:user_id>')
def edit_user(user_id):
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor(dictionary=True)
        # Query untuk mendapatkan data user berdasarkan user_id
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        return render_template('edit_user.html', user=user)
    else:
        flash('Anda tidak memiliki akses sebagai admin', 'error')
        return redirect(url_for('login'))

# Route untuk menyimpan perubahan pada user
@app.route('/admin/save_user/<int:user_id>', methods=['POST'])
def save_user(user_id):
    if 'username' in session and session['role'] == 'admin':
        username = request.form['username']
        nama = request.form['nama']
        no_hp = request.form['no_hp']
        alamat = request.form['alamat']
        role = request.form['role']
        
        cursor = db.cursor()
        # Query untuk update data user berdasarkan user_id
        cursor.execute("UPDATE users SET username = %s, nama = %s, no_hp = %s, alamat = %s, role = %s WHERE id = %s", (username, nama, no_hp, alamat, role, user_id))
        db.commit()
        flash(f'Data user dengan ID {user_id} berhasil diupdate', 'success')
    return redirect(url_for('admin_home'))

# Route untuk download CSV Users
@app.route('/admin/download_users_csv')
def download_users_csv():
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor(dictionary=True)
        
        # Hanya pilih kolom yang dibutuhkan
        cursor.execute("SELECT id, username, nama, no_hp, alamat, role FROM users")
        users = cursor.fetchall()
        
        # Membuat response dengan format CSV
        si = io.StringIO()
        cw = csv.DictWriter(si, fieldnames=['id', 'username', 'nama', 'no_hp', 'alamat', 'role'])
        cw.writeheader()
        cw.writerows(users)
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=users.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    else:
        flash('Anda tidak memiliki akses sebagai admin', 'error')
        return redirect(url_for('login'))


# Route untuk download CSV Products
@app.route('/admin/download_products_csv')
def download_products_csv():
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM device")
        products = cursor.fetchall()

        # Membuat response dengan format CSV
        si = io.StringIO()
        cw = csv.DictWriter(si, fieldnames=['id_device', 'device', 'harga'])
        cw.writeheader()
        cw.writerows(products)
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=products.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    else:
        flash('Anda tidak memiliki akses sebagai admin', 'error')
        return redirect(url_for('login'))

# Route untuk download CSV Orders
@app.route('/admin/download_orders_csv')
def download_orders_csv():
    if 'username' in session and session['role'] == 'admin':
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT sewa.id_sewa, users.username, users.no_hp, device.device, sewa.tanggal_kembali FROM sewa JOIN users ON sewa.user_id = users.id JOIN device ON sewa.device_id = device.id_device")
        orders = cursor.fetchall()
        
        # Membuat response dengan format CSV
        si = io.StringIO()
        cw = csv.DictWriter(si, fieldnames=['id_sewa', 'username', 'no_hp', 'device', 'tanggal_kembali'])
        cw.writeheader()
        cw.writerows(orders)
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=orders.csv"
        output.headers["Content-type"] = "text/csv"
        
        return output
    else:
        flash('Anda tidak memiliki akses sebagai admin', 'error')
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
