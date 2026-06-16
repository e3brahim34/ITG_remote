# README لنشر السيرفر على Render.com

## 🚀 خطوات النشر

### 1. على Render.com:

1. اذهب إلى https://render.com
2. انقر على **"New +"** ثم **"Web Service"**
3. اختر **"Deploy an existing Git repository"**
4. اربط مستودع GitHub: `e3brahim34/ITG_remote`
5. ملء البيانات:
   - **Name**: `ITG_remote-signaling`
   - **Language**: Python 3
   - **Build Command**: `pip install -r requirements-server.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT signaling_server:app`
   - **Region**: اختر الأقرب لك
   - **Instance Type**: Free (512 MB)

6. انقر **"Deploy Web Service"**

### 2. بعد النشر:

ستحصل على رابط مثل:
```
https://itg-remote-signaling.onrender.com
```

### 3. حدّث ملف الإعدادات:

عدّل `utils/signaling_config.py`:
```python
SIGNALING_SERVER_URL = 'https://itg-remote-signaling.onrender.com'
```

### 4. شغّل العميل:

```bash
# تثبيت متطلبات العميل فقط
pip install -r requirements-client.txt

# تشغيل
python main.py
```

---

## ✅ اختبار السيرفر

من المتصفح:
```
https://itg-remote-signaling.onrender.com
```

يجب أن ترى:
```json
{
  "status": "running",
  "message": "ITG Remote - Global Signaling Server",
  "devices_online": 0
}
```

---

## 🔧 الملفات المستخدمة

- `signaling_server.py` - السيرفر الرئيسي
- `requirements-server.txt` - متطلبات السيرفر (بدون GUI)
- `requirements-client.txt` - متطلبات العميل
- `Procfile` - ملف تكوين Render

---

## 📝 ملاحظات

- السيرفر يعمل بدون واجهة رسومية (Headless)
- استخدم `requirements-server.txt` فقط للسيرفر
- استخدم `requirements-client.txt` للعميل على جهازك

