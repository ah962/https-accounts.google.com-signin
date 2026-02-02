from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import re
import os
from datetime import timedelta
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(days=7)

# إعدادات إضافية
app.config['SESSION_COOKIE_SECURE'] = False  # ضع True في الإنتاج مع HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# تهيئة الإضافات
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

# نموذج المستخدم
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# إنشاء الجداول إذا لم تكن موجودة
with app.app_context():
    db.create_all()

# دوال المساعدة
def is_valid_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_strong_password(password):
    """التحقق من قوة كلمة المرور"""
    if len(password) < 8:
        return False, "كلمة المرور يجب أن تكون 8 أحرف على الأقل"
    
    if not any(c.isupper() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على حرف كبير على الأقل"
    
    if not any(c.islower() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على حرف صغير على الأقل"
    
    if not any(c.isdigit() for c in password):
        return False, "كلمة المرور يجب أن تحتوي على رقم على الأقل"
    
    return True, "كلمة المرور قوية"

# المسارات
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # معالجة طلب POST (AJAX)
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    remember = data.get('remember', False)
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'الرجاء ملء جميع الحقول'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'البريد الإلكتروني غير صالح'})
    
    # البحث عن المستخدم
    user = User.query.filter_by(email=email, is_active=True).first()
    
    if user and user.check_password(password):
        # تحديث وقت آخر دخول
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # حفظ في الجلسة
        session.permanent = remember
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.full_name
        
        return jsonify({
            'success': True,
            'message': 'تم تسجيل الدخول بنجاح',
            'user': user.to_dict(),
            'redirect': url_for('dashboard')
        })
    
    return jsonify({'success': False, 'message': 'البريد الإلكتروني أو كلمة المرور غير صحيحة'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    confirm_password = data.get('confirm_password', '')
    full_name = data.get('full_name', '').strip()
    
    # التحقق من البيانات
    if not all([email, password, confirm_password, full_name]):
        return jsonify({'success': False, 'message': 'الرجاء ملء جميع الحقول'})
    
    if not is_valid_email(email):
        return jsonify({'success': False, 'message': 'البريد الإلكتروني غير صالح'})
    
    password_valid, password_message = is_strong_password(password)
    if not password_valid:
        return jsonify({'success': False, 'message': password_message})
    
    if password != confirm_password:
        return jsonify({'success': False, 'message': 'كلمات المرور غير متطابقة'})
    
    # التحقق إذا كان البريد موجود مسبقاً
    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'message': 'البريد الإلكتروني مسجل مسبقاً'})
    
    # إنشاء مستخدم جديد
    try:
        new_user = User(email=email, full_name=full_name)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.',
            'redirect': url_for('login')
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'})

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('الرجاء تسجيل الدخول أولاً')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=user)

@app.route('/api/check-auth')
def check_auth():
    """فحص حالة المصادقة (للاستخدام من قبل JavaScript)"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': user.to_dict()
            })
    
    return jsonify({'authenticated': False})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/api/validate-email', methods=['POST'])
def validate_email():
    """التحقق من صحة البريد الإلكتروني"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'valid': False, 'message': 'البريد الإلكتروني مطلوب'})
    
    if not is_valid_email(email):
        return jsonify({'valid': False, 'message': 'صيغة البريد الإلكتروني غير صحيحة'})
    
    # التحقق إذا كان البريد مستخدم مسبقاً
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'valid': False, 'message': 'البريد الإلكتروني مسجل مسبقاً'})
    
    return jsonify({'valid': True, 'message': 'البريد الإلكتروني صالح'})

@app.route('/api/validate-password', methods=['POST'])
def validate_password():
    """التحقق من قوة كلمة المرور"""
    data = request.get_json()
    password = data.get('password', '')
    
    valid, message = is_strong_password(password)
    return jsonify({'valid': valid, 'message': message})

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
