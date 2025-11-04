from flask import Flask, request, jsonify, redirect, render_template
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = '/data/urls.db'

def init_db():
    """Initialize the SQLite database"""
    os.makedirs('/data', exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clicks INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def generate_short_code(url):
    """Generate a short code from URL using MD5 hash"""
    return hashlib.md5(url.encode()).hexdigest()[:8]

@app.route('/')
def index():
    """Home page with URL shortening form"""
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten a URL"""
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url']
    
    # Validate URL format
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check if URL already exists
        c.execute('SELECT short_code FROM urls WHERE original_url = ?', (original_url,))
        existing = c.fetchone()
        
        if existing:
            short_code = existing[0]
        else:
            # Generate unique short code
            short_code = generate_short_code(original_url)
            
            # Ensure uniqueness
            attempts = 0
            while attempts < 5:
                c.execute('SELECT id FROM urls WHERE short_code = ?', (short_code,))
                if not c.fetchone():
                    break
                short_code = hashlib.md5((original_url + str(attempts)).encode()).hexdigest()[:8]
                attempts += 1
            
            # Insert new URL
            c.execute(
                'INSERT INTO urls (original_url, short_code) VALUES (?, ?)',
                (original_url, short_code)
            )
        
        conn.commit()
        short_url = f"{request.host_url}{short_code}"
        
        return jsonify({
            'original_url': original_url,
            'short_url': short_url,
            'short_code': short_code
        })
        
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Failed to generate unique short code'}), 500
    finally:
        conn.close()

@app.route('/<short_code>')
def redirect_to_url(short_code):
    """Redirect to original URL using short code"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            'UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?',
            (short_code,)
        )
        c.execute(
            'SELECT original_url FROM urls WHERE short_code = ?', 
            (short_code,)
        )
        result = c.fetchone()
        
        conn.commit()
        conn.close()
        
        if result:
            return redirect(result[0])
        else:
            return jsonify({'error': 'Short URL not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats/<short_code>')
def get_stats(short_code):
    """Get statistics for a short URL"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute(
            'SELECT original_url, short_code, created_at, clicks FROM urls WHERE short_code = ?',
            (short_code,)
        )
        result = c.fetchone()
        conn.close()
        
        if result:
            return jsonify({
                'original_url': result[0],
                'short_code': result[1],
                'created_at': result[2],
                'clicks': result[3]
            })
        else:
            return jsonify({'error': 'Short URL not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stats')
def all_stats():
    """Get all URLs and their stats"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('SELECT original_url, short_code, created_at, clicks FROM urls ORDER BY created_at DESC')
        urls = c.fetchall()
        conn.close()
        
        stats = []
        for url in urls:
            stats.append({
                'original_url': url[0],
                'short_code': url[1],
                'created_at': url[2],
                'clicks': url[3],
                'short_url': f"{request.host_url}{url[1]}"
            })
        
        return jsonify({'urls': stats, 'total': len(stats)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)