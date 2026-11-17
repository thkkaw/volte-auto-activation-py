import os
import stat
from dotenv import load_dotenv

load_dotenv()

gcon_workers = int(os.getenv('GCON_WORKERS', 8))
sock_name = os.getenv('SOCK_NAME', 'app')

bind = f'unix:{sock_name}.sock'
workers = gcon_workers
errorlog = 'logs/sock/error.log'
loglevel = 'info'
accesslog = 'logs/sock/access.log'
chmod_socket = stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO