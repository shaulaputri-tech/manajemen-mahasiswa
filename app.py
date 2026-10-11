from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "kunci-rahasia-kampus"

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mahasiswa (
            nim INTEGER PRIMARY KEY,
            nama TEXT NOT NULL,
            program_studi TEXT NOT NULL,
            angkatan INTEGER NOT NULL,
            ipk REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = get_db_connection()
    mahasiswa_list = conn.execute('SELECT * FROM mahasiswa').fetchall()
    conn.close()
    
    tahun_sekarang = datetime.now().year
    data_mahasiswa = []
    for mhs in mahasiswa_list:
        lama_studi = tahun_sekarang - mhs['angkatan']
        mhs_dict = dict(mhs)
        mhs_dict['lama_studi'] = lama_studi if lama_studi >= 0 else 0
        data_mahasiswa.append(mhs_dict)
        
    return render_template('index.html', mahasiswa=data_mahasiswa)

@app.route('/tambah', methods=('GET', 'POST'))
def tambah():
    if request.method == 'POST':
        nim = request.form['nim']
        nama = request.form['nama'].strip()
        program_studi = request.form['program_studi'].strip()
        angkatan = request.form['angkatan']
        ipk = request.form['ipk']
        
        if not nim or not nama or not program_studi or not angkatan or not ipk:
            flash('Semua field wajib diisi!', 'danger')
            return redirect(url_for('tambah'))
        
        try:
            nim_int = int(nim)
            angkatan_int = int(angkatan)
            ipk_float = float(ipk)
        except ValueError:
            flash('NIM, Angkatan, dan IPK harus berupa angka!', 'danger')
            return redirect(url_for('tambah'))
            
        if not (0.00 <= ipk_float <= 4.00):
            flash('IPK harus berada di rentang 0.00 sampai 4.00!', 'danger')
            return redirect(url_for('tambah'))
            
        conn = get_db_connection()
        existing_nim = conn.execute('SELECT nim FROM mahasiswa WHERE nim = ?', (nim_int,)).fetchone()
        if existing_nim:
            conn.close()
            flash(f'NIM {nim_int} sudah terdaftar di sistem!', 'danger')
            return redirect(url_for('tambah'))
            
        conn.execute('INSERT INTO mahasiswa (nim, nama, program_studi, angkatan, ipk) VALUES (?, ?, ?, ?, ?)',
                     (nim_int, nama, program_studi, angkatan_int, ipk_float))
        conn.commit()
        conn.close()
        
        flash('Data mahasiswa berhasil ditambahkan!', 'success')
        return redirect(url_for('index'))
        
    return render_template('tambah.html')

@app.route('/edit/<int:nim>', methods=('GET', 'POST'))
def edit(nim):
    conn = get_db_connection()
    mhs = conn.execute('SELECT * FROM mahasiswa WHERE nim = ?', (nim,)).fetchone()
    
    if mhs is None:
        conn.close()
        flash('Data mahasiswa tidak ditemukan!', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        nama = request.form['nama'].strip()
        program_studi = request.form['program_studi'].strip()
        angkatan = request.form['angkatan']
        ipk = request.form['ipk']
        
        if not nama or not program_studi or not angkatan or not ipk:
            flash('Semua field wajib diisi!', 'danger')
            return redirect(url_for('edit', nim=nim))
            
        try:
            angkatan_int = int(angkatan)
            ipk_float = float(ipk)
        except ValueError:
            flash('Angkatan dan IPK harus berupa angka!', 'danger')
            return redirect(url_for('edit', nim=nim))
            
        if not (0.00 <= ipk_float <= 4.00):
            flash('IPK harus berada di rentang 0.00 sampai 4.00!', 'danger')
            return redirect(url_for('edit', nim=nim))
            
        conn.execute('UPDATE mahasiswa SET nama = ?, program_studi = ?, angkatan = ?, ipk = ? WHERE nim = ?',
                     (nama, program_studi, angkatan_int, ipk_float, nim))
        conn.commit()
        conn.close()
        
        flash('Data mahasiswa berhasil diperbarui!', 'success')
        return redirect(url_for('index'))
        
    conn.close()
    return render_template('edit.html', mahasiswa=mhs)

@app.route('/hapus/<int:nim>', methods=('POST',))
def hapus(nim):
    conn = get_db_connection()
    conn.execute('DELETE FROM mahasiswa WHERE nim = ?', (nim,))
    conn.commit()
    conn.close()
    flash('Data mahasiswa berhasil dihapus!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)