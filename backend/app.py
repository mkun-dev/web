# backend/app.py (最终简化版)

import os
from flask import (Flask, jsonify, request, render_template,
                   redirect, url_for, flash, session)
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# --- 基础配置 ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'a_very_secret_key_that_you_should_change'

# --- 数据库配置 ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- 文件上传配置 ---
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- 数据库模型 (AboutContent 已简化) ---
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    alt = db.Column(db.String(100), nullable=False)

class AboutContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False) # <--- 修改点
    email = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String(200), nullable=False)


# --- 登录状态检查的装饰器 ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('请先登录。', 'warning')
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function


# --- 前端页面路由 ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


# --- 前端 API 接口 (About API 已简化) ---
@app.route('/api/about', methods=['GET'])
def get_about_data():
    content = db.session.get(AboutContent, 1)
    if content:
        final_image_url = url_for('static', filename=content.imageUrl)
        return jsonify({
            "content": content.content, # <--- 修改点
            "email": content.email,
            "imageUrl": final_image_url
        })
    return jsonify({"error": "Content not found"}), 404

@app.route('/api/photos', methods=['GET'])
def get_photos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 6, type=int)
    pagination = Photo.query.order_by(Photo.id.desc()).paginate(page=page, per_page=limit, error_out=False)
    
    photos_with_full_url = []
    for p in pagination.items:
        final_url = url_for('static', filename=p.url)
        photos_with_full_url.append({"id": p.id, "url": final_url, "alt": p.alt})

    return jsonify({
        "photos": photos_with_full_url,
        "total_photos": pagination.total,
        "current_page": pagination.page,
        "total_pages": pagination.pages
    })


# --- 后台管理核心逻辑 (About 更新逻辑已简化) ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('用户名或密码错误。', 'danger')
    return render_template('login.html')

@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    about_content = db.session.get(AboutContent, 1)
    all_photos = Photo.query.order_by(Photo.id.desc()).all()
    return render_template('admin.html', about=about_content, photos=all_photos)

@app.route('/admin/logout')
@login_required
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login_page'))

@app.route('/admin/about', methods=['POST'])
@login_required
def update_about():
    content = db.session.get(AboutContent, 1)
    if content:
        content.content = request.form.get('content') # <--- 修改点
        content.email = request.form.get('email')
        content.imageUrl = request.form.get('imageUrl')
        db.session.commit()
        flash('“关于我”页面内容已更新！', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/photos/upload', methods=['POST'])
@login_required
def upload_photo():
    # (代码无变化)
    if 'file' not in request.files:
        flash('请求中没有文件部分', 'danger')
        return redirect(url_for('admin_dashboard'))
    file = request.files['file']
    alt_text = request.form.get('alt')
    if file.filename == '' or not alt_text:
        flash('没有选择文件或未填写描述', 'danger')
        return redirect(url_for('admin_dashboard'))
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        db_path = os.path.join('uploads', filename)
        new_photo = Photo(url=db_path, alt=alt_text)
        db.session.add(new_photo)
        db.session.commit()
        flash('照片上传成功！', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/photos/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    # (代码无变化)
    photo = db.session.get(Photo, photo_id)
    if photo:
        if photo.url.startswith('uploads/'):
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(photo.url))
                if os.path.exists(filepath):
                    os.remove(filepath)
            except OSError as e:
                flash(f"删除文件失败: {e}", "danger")
        db.session.delete(photo)
        db.session.commit()
        flash('照片已删除。', 'success')
    return redirect(url_for('admin_dashboard'))


# --- 数据库初始化命令 (About 初始化已简化) ---
@app.cli.command("db-init")
def db_init():
    with app.app_context():
        db.create_all()
        
        if not Admin.query.first():
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            new_admin = Admin(username='admin', password_hash=hashed_password)
            db.session.add(new_admin)
            print("Created default admin user (username=admin, password=admin).")

        if not AboutContent.query.first():
            initial_about = AboutContent(
                id=1,
                content="你好，我是朱泽宇。我是一名来自西安的摄影爱好者，热衷于通过镜头捕捉日常生活中的平凡之美。对我而言，摄影不仅是技术的展现，更是情感的表达和故事的讲述。", # <--- 修改点
                email="1109004016@qq.com",
                imageUrl="src/images/sb01.webp"
            )
            db.session.add(initial_about)
            print("Added initial about content.")

        if not Photo.query.first():
            initial_photos = [Photo(url="src/images/sb00.png", alt="作品一")]
            db.session.add_all(initial_photos)
            print("Added initial photos.")

        db.session.commit()
        print("Database initialized!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)