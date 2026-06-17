"""Global Signaling Server - يعمل على Render.com"""
import eventlet
eventlet.monkey_patch()

import os
from datetime import datetime
import logging
from flask import Flask, request
from flask_socketio import SocketIO, emit

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'itg_remote_secret_key')
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25
)

# متخزن الأجهزة
devices = {}

def get_clean_ip():
    """وظيفة لاستخراج الـ IP الحقيقي للمستخدم وتجاوز بروكسي Render"""
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip and ',' in ip:
        # نأخذ أول عنوان فقط ونحذف أي مسافات
        return ip.split(',')[0].strip()
    return ip

logger.info("🚀 Global Signaling Server Started")

# ==================== Socket.IO Events ====================

@socketio.on('connect')
def handle_connect():
    logger.info(f"✓ Client connected: {request.sid}")
    emit('response', {'data': 'Connected to signaling server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"✗ Client disconnected: {request.sid}")
    for device_id in list(devices.keys()):
        if devices[device_id].get('session_id') == request.sid:
            del devices[device_id]
            emit('device_unregistered', {'device_id': device_id}, broadcast=True)
            logger.info(f"✗ Device unregistered: {device_id}")

@socketio.on('register_device')
def handle_register_device(data):
    try:
        device_id = data.get('device_id')
        device_name = data.get('device_name', 'Unknown Device')
        port = data.get('port', 25557)
        
        if not device_id:
            emit('error', {'message': 'device_id is required'})
            return

        # تنظيف الـ IP قبل الحفظ
        public_ip = get_clean_ip()
        
        device_info = {
            'device_id': device_id,
            'device_name': device_name,
            'port': port,
            'session_id': request.sid,
            'public_ip': public_ip,
            'timestamp': datetime.now().isoformat()
        }
        
        devices[device_id] = device_info
        logger.info(f"✓ Device registered: {device_name} from IP: {public_ip}")
        
        emit('device_registered', {
            'device': device_info,
            'devices_online': len(devices)
        }, broadcast=True)
        
    except Exception as e:
        logger.error(f"! Error in register_device: {str(e)}")

@socketio.on('get_devices')
def handle_get_devices():
    emit('device_list', {
        'devices': list(devices.values()),
        'count': len(devices),
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('initiate_p2p')
def handle_p2p(data):
    """إرسال طلب P2P مع تنظيف الـ IP لضمان عمل الـ Hole Punching"""
    target_id = data.get('target_id')
    if target_id in devices:
        # تنظيف IP المرسل (الحاكم) قبل إرساله للمستقبل (المحكوم)
        sender_ip = get_clean_ip()
        
        emit('p2p_request', {
            'sender_id': data.get('sender_id'),
            'sender_public_ip': sender_ip, # هنا تم الإصلاح
            'sender_udp_port': data.get('udp_port')
        }, room=devices[target_id]['session_id'])
        logger.info(f"P2P Signal forwarded from {sender_ip} to {target_id}")

# ==================== REST API & Health ====================

@app.route('/')
def index():
    return {
        'status': 'running',
        'devices_online': len(devices),
        'timestamp': datetime.now().isoformat()
    }, 200

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
