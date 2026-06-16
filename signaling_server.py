"""Global Signaling Server - يعمل على Render.com"""
from flask import Flask, request
from flask_socketio import SocketIO, emit, disconnect
import json
import time
from datetime import datetime
import os
import logging

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'itg_remote_secret_key')
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',  # استخدام threading بدل eventlet
    ping_timeout=60,
    ping_interval=25
)

# متخزن الأجهزة
devices = {}
connections_log = []

logger.info("🚀 Global Signaling Server Started")

# ==================== Socket.IO Events ====================

@socketio.on('connect')
def handle_connect():
    """تعامل مع الاتصال الجديد"""
    logger.info(f"✓ Client connected: {request.sid}")
    emit('response', {'data': 'Connected to signaling server'})

@socketio.on('disconnect')
def handle_disconnect():
    """تعامل مع قطع الاتصال"""
    logger.info(f"✗ Client disconnected: {request.sid}")
    
    # إزالة الجهاز من القائمة
    for device_id in list(devices.keys()):
        if devices[device_id].get('session_id') == request.sid:
            del devices[device_id]
            emit('device_unregistered', {'device_id': device_id}, broadcast=True, skip_sid=request.sid)
            logger.info(f"✗ Device unregistered: {device_id}")

@socketio.on('register_device')
def handle_register_device(data):
    """تسجيل جهاز جديد"""
    try:
        device_id = data.get('device_id')
        device_name = data.get('device_name')
        port = data.get('port')
        
        if not device_id or not device_name:
            emit('error', {'message': 'Missing device_id or device_name'})
            return
        
        # حفظ بيانات الجهاز
        device_info = {
            'device_id': device_id,
            'device_name': device_name,
            'port': port,
            'session_id': request.sid,
            'remote_addr': request.remote_addr,
            'timestamp': datetime.now().isoformat(),
            'public_ip': request.remote_addr,
        }
        
        devices[device_id] = device_info
        
        logger.info(f"✓ Device registered: {device_name} ({device_id}) from {request.remote_addr}")
        
        # إرسال إشعار لجميع الأجهزة
        emit('device_registered', {
            'device': device_info,
            'devices_online': len(devices)
        }, broadcast=True)
        
        # تسجيل في السجل
        connections_log.append({
            'action': 'register',
            'device_id': device_id,
            'device_name': device_name,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"! Error registering device: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('get_devices')
def handle_get_devices():
    """الحصول على قائمة الأجهزة المتاحة"""
    try:
        devices_list = list(devices.values())
        emit('device_list', {
            'devices': devices_list,
            'count': len(devices_list),
            'timestamp': datetime.now().isoformat()
        })
        logger.info(f"i Device list requested: {len(devices_list)} devices online")
    except Exception as e:
        logger.error(f"! Error getting devices: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('unregister_device')
def handle_unregister_device(data):
    """إلغاء تسجيل جهاز"""
    try:
        device_id = data.get('device_id')
        
        if device_id in devices:
            device_name = devices[device_id].get('device_name')
            del devices[device_id]
            
            logger.info(f"✗ Device unregistered: {device_name} ({device_id})")
            
            # إرسال إشعار
            emit('device_unregistered', {
                'device_id': device_id,
                'devices_online': len(devices)
            }, broadcast=True)
            
            # تسجيل
            connections_log.append({
                'action': 'unregister',
                'device_id': device_id,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"! Error unregistering device: {str(e)}")
        emit('error', {'message': str(e)})

@socketio.on('heartbeat')
def handle_heartbeat(data):
    """تحديث حالة الجهاز (Keep-Alive)"""
    device_id = data.get('device_id')
    if device_id in devices:
        devices[device_id]['last_heartbeat'] = datetime.now().isoformat()
        devices[device_id]['session_id'] = request.sid

# ==================== REST API Endpoints ====================

@app.route('/', methods=['GET'])
def index():
    """الصفحة الرئيسية"""
    return {
        'status': 'running',
        'message': 'ITG Remote - Global Signaling Server',
        'version': '1.0',
        'devices_online': len(devices),
        'timestamp': datetime.now().isoformat()
    }, 200

@app.route('/api/devices', methods=['GET'])
def api_get_devices():
    """الحصول على قائمة الأجهزة عبر REST"""
    return {
        'devices': list(devices.values()),
        'count': len(devices),
        'timestamp': datetime.now().isoformat()
    }, 200

@app.route('/api/devices/<device_id>', methods=['GET'])
def api_get_device(device_id):
    """الحصول على معلومات جهاز معين"""
    if device_id in devices:
        return {'device': devices[device_id]}, 200
    return {'error': 'Device not found'}, 404

@app.route('/api/status', methods=['GET'])
def api_status():
    """حالة السيرفر"""
    return {
        'status': 'running',
        'devices_online': len(devices),
        'timestamp': datetime.now().isoformat(),
        'uptime': 'running'
    }, 200

@app.route('/health', methods=['GET'])
def health():
    """اختبار صحة السيرفر (لـ Render)"""
    return {'status': 'healthy'}, 200

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

# ==================== Main ====================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting ITG Remote Signaling Server on port {port}")
    logger.info(f"📡 WebSocket: ws://localhost:{port}")
    logger.info(f"🌐 HTTP: http://localhost:{port}\n")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=False
    )
