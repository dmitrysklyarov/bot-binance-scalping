import os

os.system("nohup gunicorn --workers 1 wsgi:app &")
os.system("nohup python3 -u run.py &")