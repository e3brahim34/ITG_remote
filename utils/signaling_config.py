"""Global Signaling Server Configuration"""

# Render.com Server URL (استخدم سيرفرك الخاص)
SIGNALING_SERVER_URL = 'https://iron-signaling.onrender.com'

# Alternative backup servers
BACKUP_SERVERS = [
    'https://iron-signaling.onrender.com',
    # أضف سيرفرات احتياطية هنا
]

# Discovery settings
DISCOVERY_INTERVAL = 2.0  # ثانية
DISCOVERY_TIMEOUT = 10.0  # ثانية

# P2P Connection settings
P2P_TIMEOUT = 30.0  # ثانية
P2P_BUFFER_SIZE = 65536  # بايت

# NAT Traversal
STUN_SERVERS = [
    'stun.l.google.com:19302',
    'stun1.l.google.com:19302',
]

# Local settings
LOCAL_DISCOVERY_ENABLED = True
LOCAL_DISCOVERY_PORT = 25555
