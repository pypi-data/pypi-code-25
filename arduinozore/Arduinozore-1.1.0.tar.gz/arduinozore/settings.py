"""Settings module."""
import os


def path(root, *a):
    """Build path from root."""
    return os.path.join(root, *a)


ROOT = os.path.dirname(
    os.path.abspath(__file__))

CONFIG_FOLDER = path(os.path.expanduser("~"), '.arduinozore')

TEMPLATE_FOLDER = path(ROOT, 'templates/')
CERT_FOLDER = path(CONFIG_FOLDER, 'certs/')
STATIC_PATH = path(CONFIG_FOLDER, 'static/')
STATIC_INSTALLER_PATH = path(ROOT, 'static_installer.sh')
CERT_INSTALLER_PATH = path(ROOT, 'install_cert.sh')

PORT = 8000
SSL_PORT = 8001

ssl_opts = {
    "certfile": path(CERT_FOLDER, "myserver.crt.pem"),
    "keyfile": path(CERT_FOLDER, "myserver.crt.key"),
}

settings = {'debug': True,
            'static_path': STATIC_PATH}
DEVICE_CONFIG_FOLDER = path(CONFIG_FOLDER, 'device')
SENSOR_CONFIG_FOLDER = path(CONFIG_FOLDER, 'sensor')
CARD_CONFIG_FOLDER = path(CONFIG_FOLDER, 'card')

ARDUINO_CODE_FILE_NAME = 'arduinozore.ino'
ARDUINO_FILE_PATH = path(ROOT, '..', 'arduino',
                         'arduinozore', ARDUINO_CODE_FILE_NAME)
