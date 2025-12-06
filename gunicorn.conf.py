import multiprocessing

workers = multiprocessing.cpu_count() * 2
threads = 2
bind = "0.0.0.0:8000"

wsgi_app = "server.wsgi:application"
