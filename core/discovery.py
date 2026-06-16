import socketio
import threading
from utils.logger import Logger

logger = Logger(__name__)

class DeviceDiscovery:
    def __init__(self, device_id, device_name):
        self.device_id = device_id
        self.device_name = device_name
        self.sio = socketio.Client()
        self.discovered_devices = {}
        self.on_device_found = None
        
        # تعريف الأحداث القادمة من سيرفر Render
        @self.sio.on('discover_response')
        def on_discover(data):
            devices_list = data.get('devices', [])
            for dev in devices_list:
                if dev['device_id'] != self.device_id:
                    # إضافة الـ IP العام الذي وفره السيرفر
                    if dev['device_id'] not in self.discovered_devices:
                        self.discovered_devices[dev['device_id']] = dev
                        if self.on_device_found:
                            self.on_device_found(dev)

    def start_broadcast(self, port=25557, server_url='https://iron-signaling.onrender.com'):
        try:
            if not self.sio.connected:
                self.sio.connect(server_url, wait_timeout=20)
            
            # نرسل البيانات كـ Dictionary مسطح لسهولة القراءة
            self.sio.emit('register', {
                'device_id': self.device_id,
                'device_info': {
                    'device_id': self.device_id,
                    'name': self.device_name, # تأكد أن هذا المتغير ليس None
                    'port': port
                }
            })
            print(f"DEBUG: Registered as {self.device_name}")
        except Exception as e:
            print(f"Register error: {e}")
    
    def start_discovery(self, server_url='https://iron-signaling.onrender.com'):
        """البدء في طلب قائمة الأجهزة من السيرفر العالمي كل 5 ثواني"""
        try:
            if not self.sio.connected:
                self.sio.connect(server_url)
            
            def refresh_loop():
                while self.sio.connected:
                    self.sio.emit('discover')
                    self.sio.sleep(5)
            
            threading.Thread(target=refresh_loop, daemon=True).start()
            logger.info("Global Discovery Started")
        except Exception as e:
            logger.error(f"Global Discovery Error: {e}")

    def get_discovered_devices(self):
        return self.discovered_devices