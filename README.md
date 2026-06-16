# ITG Remote - تطبيق التحكم عن بعد بالأجهزة

تطبيق احترافي للتحكم عن بعد بأجهزة Windows عبر شبكة محلية (LAN) مع تشفير كامل وواجهات رسومية متقدمة.

## ✨ الميزات الرئيسية

- 🔗 **اتصال P2P مباشر** بدون وسيط بعد الاكتشاف
- 📸 **بث صور الشاشة** بشكل متكرر وفعال
- 🖱️ **التحكم الكامل** بالماوس والكيبورد
- 🔐 **تشفير AES-256** لجميع الاتصالات
- 🌐 **شبكات محلية (LAN)**
- 📊 **لوحة تحكم احترافية** بـ PyQt5
- 💾 **سجل الاتصالات** في قاعدة بيانات SQLite
- ⚡ **أداء عالي** مع ضغط الصور

## 📁 هيكل المشروع

```
ITG_remote/
├── core/
│   ├── __init__.py
│   ├── encryption.py          # نظام التشفير AES-256
│   ├── connection.py          # إدارة الاتصلات P2P
│   ├── screen_capture.py      # التقاط الشاشة
│   ├── input_controller.py    # التحكم بالماوس والكيبورد
│   └── discovery.py           # آلية اكتشاف الأجهزة
├── server/
│   ├── __init__.py
│   ├── discovery_server.py    # سيرفر الاكتشاف
│   └── config.py
├── client/
│   ├── __init__.py
│   ├── controlled_device.py   # عميل المحكوم
│   └── controller_device.py   # عميل المتحكم
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   ├── controller_ui.py       # واجهة المتحكم
│   ├── controlled_ui.py       # واجهة المحكوم
│   └── styles.py              # تصاميم PyQt5
├── database/
│   ├── __init__.py
│   ├── db_manager.py          # إدارة قاعدة البيانات
│   └── schema.sql
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── helpers.py
│   └── config.py
├── main.py                     # نقطة البداية
├── requirements.txt
└── README.md
```

## 🚀 الخطوات البدائية

### 1. التثبيت
```bash
git clone https://github.com/e3brahim34/ITG_remote.git
cd ITG_remote
pip install -r requirements.txt
```

### 2. تشغيل سيرفر الاكتشاف
```bash
python server/discovery_server.py
```

### 3. تشغيل الجهاز المحكوم
```bash
python client/controlled_device.py
```

### 4. تشغيل الجهاز المتحكم
```bash
python client/controller_device.py
```

## 📊 المتطلبات

- Python 3.8+
- Windows 10/11
- شبكة محلية (LAN)

## 👨‍💻 المطور

تم التطوير بواسطة: e3brahim34
