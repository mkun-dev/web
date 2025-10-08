# backend/app.py (最终后台功能版)

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
# 图片将保存在 backend/static/uploads/ 文件夹中
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 确保文件夹存在
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# --- 数据库模型 (新增 Admin 模型) ---
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # url 现在存储的是相对于 static 文件夹的路径，例如 'uploads/my_photo.jpg'
    url = db.Column(db.String(200), nullable=False)
    alt = db.Column(db.String(100), nullable=False)


class AboutContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    paragraph1 = db.Column(db.Text, nullable=False)
    paragraph2 = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String(200), nullable=False)


# --- 登录状态检查的装饰器 ---
def login_required(f):
    """一个自定义的装饰器，用于保护需要登录才能访问的路由。"""

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
# --- 前端 API 接口---
@app.route('/api/about', methods=['GET'])
def get_about_data():
    content = db.session.get(AboutContent, 1)
    if content:
        # 统一为图片生成正确的 /static/... 路径
        final_image_url = url_for('static', filename=content.imageUrl)

        return jsonify({
            "paragraph1": content.paragraph1,
            "paragraph2": content.paragraph2,
            "email": content.email,
            "imageUrl": final_image_url
        })
    return jsonify({"error": "Content not found"}), 404


@app.route('/api/photos', methods=['GET'])
def get_photos():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 6, type=int)
    pagination = Photo.query.order_by(Photo.id.desc()).paginate(page=page, per_page=limit, error_out=False)

    # 为前端API返回完整的URL
    photos_with_full_url = []
    for p in pagination.items:
        # 统一为所有照片生成正确的 /static/... 路径
        final_url = url_for('static', filename=p.url)
        photos_with_full_url.append({"id": p.id, "url": final_url, "alt": p.alt})

    return jsonify({
        "photos": photos_with_full_url,
        "total_photos": pagination.total,
        "current_page": pagination.page,
        "total_pages": pagination.pages
    })


# --- 后台管理核心逻辑 ---

# [GET] 显示登录页
@app.route('/admin/login', methods=['GET'])
def admin_login_page():
    return render_template('login.html')


# [POST] 处理登录请求
@app.route('/admin/login', methods=['POST'])
def handle_admin_login():
    username = request.form.get('username')
    password = request.form.get('password')
    admin = Admin.query.filter_by(username=username).first()

    if admin and check_password_hash(admin.password_hash, password):
        session['admin_logged_in'] = True
        session['username'] = admin.username
        flash('登录成功！', 'success')
        return redirect(url_for('admin_dashboard'))
    else:
        flash('用户名或密码错误。', 'danger')
        return redirect(url_for('admin_login_page'))


# [GET] 显示管理主页 (受保护)
@app.route('/admin', methods=['GET'])
@login_required
def admin_dashboard():
    about_content = db.session.get(AboutContent, 1)
    all_photos = Photo.query.order_by(Photo.id.desc()).all()
    return render_template('admin.html', about=about_content, photos=all_photos)


# [GET] 退出登录
@app.route('/admin/logout')
@login_required
def admin_logout():
    session.clear()
    flash('您已成功退出。', 'info')
    return redirect(url_for('admin_login_page'))


# [POST] 更新“关于我”内容 (受保护)
@app.route('/admin/about', methods=['POST'])
@login_required
def update_about():
    content = db.session.get(AboutContent, 1)
    if content:
        content.paragraph1 = request.form.get('paragraph1')
        content.paragraph2 = request.form.get('paragraph2')
        content.email = request.form.get('email')
        content.imageUrl = request.form.get('imageUrl')  # 允许手动修改图片路径
        db.session.commit()
        flash('“关于我”页面内容已更新！', 'success')
    else:
        flash('未找到内容记录，更新失败。', 'danger')
    return redirect(url_for('admin_dashboard'))


# [POST] 上传新照片 (受保护)
@app.route('/admin/photos/upload', methods=['POST'])
@login_required
def upload_photo():
    if 'file' not in request.files:
        flash('请求中没有文件部分', 'danger')
        return redirect(url_for('admin_dashboard'))

    file = request.files['file']
    alt_text = request.form.get('alt')

    if file.filename == '' or not alt_text:
        flash('没有选择文件或未填写描述', 'danger')
        return redirect(url_for('admin_dashboard'))

    if file:
        filename = file.filename  # 在生产环境中应使用安全的文件名
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # 数据库中存储相对于 static 目录的路径
        db_path = os.path.join('uploads', filename)

        new_photo = Photo(url=db_path, alt=alt_text)
        db.session.add(new_photo)
        db.session.commit()
        flash('照片上传成功！', 'success')

    return redirect(url_for('admin_dashboard'))


# [POST] 删除照片 (受保护)
@app.route('/admin/photos/delete/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = db.session.get(Photo, photo_id)
    if photo:
        # 只有当图片在 uploads 文件夹时才尝试删除文件
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
    else:
        flash('未找到该照片。', 'danger')

    return redirect(url_for('admin_dashboard'))


# --- 数据库初始化命令 (新增 Admin 用户) ---
@app.cli.command("db-init")
def db_init():
    with app.app_context():
        db.create_all()

        if not Admin.query.first():
            # 创建一个默认管理员账户
            # 密码是 'admin'
            hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
            new_admin = Admin(username='admin', password_hash=hashed_password)
            db.session.add(new_admin)
            print("Created default admin user (username=admin, password=admin).")

        # ... (填充 About 和 Photo 的代码保持不变)
        if not AboutContent.query.first():
            initial_about = AboutContent(id=1, paragraph1="你好...", paragraph2="我是一名...", email="123@qq.com",
                                         imageUrl="src/images/sb01.webp")
            db.session.add(initial_about)
        if not Photo.query.first():
            initial_photos = [Photo(url="src/images/sb00.png", alt="作品一")]
            db.session.add_all(initial_photos)

        db.session.commit()
        print("Database initialized!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)