// التحقق من حالة المصادقة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', async function() {
    // التحقق من حالة المستخدم
    try {
        const response = await fetch('/api/check-auth');
        const data = await response.json();
        
        if (data.authenticated) {
            console.log('المستخدم مسجل الدخول:', data.user);
            // تحديث واجهة المستخدم إذا لزم الأمر
        }
    } catch (error) {
        console.error('خطأ في التحقق من حالة المصادقة:', error);
    }
    
    // إضافة تأثيرات للرسائل
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((message, index) => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateX(100%)';
            setTimeout(() => message.remove(), 300);
        }, 5000 + (index * 1000));
    });
    
    // إضافة تأثيرات للأزرار
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mousedown', () => {
            button.style.transform = 'scale(0.95)';
        });
        
        button.addEventListener('mouseup', () => {
            button.style.transform = '';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.transform = '';
        });
    });
    
    // إضافة تأثير للبطاقات
    const cards = document.querySelectorAll('.feature-card, .dashboard-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', () => {
            card.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });
});

// وظيفة لعرض رسائل التنبيه
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `flash-message ${type}`;
    alertDiv.textContent = message;
    
    const flashContainer = document.querySelector('.flash-messages') || createFlashContainer();
    flashContainer.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        alertDiv.style.transform = 'translateX(100%)';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// إنشاء حاوية للرسائل إذا لم تكن موجودة
function createFlashContainer() {
    const container = document.createElement('div');
    container.className = 'flash-messages';
    document.body.appendChild(container);
    return container;
}

// التحقق من صحة البريد الإلكتروني
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// التحقق من قوة كلمة المرور
function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength += 25;
    if (/[A-Z]/.test(password)) strength += 25;
    if (/[a-z]/.test(password)) strength += 25;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 10;
    
    return Math.min(strength, 100);
}

// تسجيل الخروج
async function logout() {
    try {
        const response = await fetch('/logout');
        if (response.ok) {
            window.location.href = '/';
        }
    } catch (error) {
        console.error('خطأ في تسجيل الخروج:', error);
    }
}

// منع إرسال النماذج بالضغط على Enter في الحقول غير النصية
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && !e.target.type.includes('text')) {
        e.preventDefault();
    }
});

// وظائف مساعدة للأرقام العربية
function toArabicNumbers(num) {
    const arabicNumbers = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    return num.toString().replace(/\d/g, digit => arabicNumbers[digit]);
}

// تحسين تجربة المستخدم على الأجهزة المحمولة
if ('ontouchstart' in window) {
    document.body.classList.add('touch-device');
}

// الكشف عن الاتصال بالإنترنت
window.addEventListener('online', () => {
    showAlert('تم استعادة الاتصال بالإنترنت', 'success');
});

window.addEventListener('offline', () => {
    showAlert('فقدان الاتصال بالإنترنت', 'error');
});
