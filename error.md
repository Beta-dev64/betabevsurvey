 
 
      
  File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open

    return open_func(self.baseFilename, self.mode,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PermissionError: [Errno 13] Permission denied: '/app/logs/dangote_app.log'

[2026-01-19 17:48:46 +0000] [6] [INFO] Worker exiting (pid: 6)

[2026-01-19 17:48:46 +0000] [7] [ERROR] Exception in worker process

Traceback (most recent call last):

  File "/usr/local/lib/python3.11/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker

    worker.init_process()

  File "/usr/local/lib/python3.11/site-packages/gunicorn/workers/base.py", line 135, in init_process

    self.load_wsgi()

  File "/usr/local/lib/python3.11/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi

    self.wsgi = self.app.wsgi()

                ^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/base.py", line 66, in wsgi

    self.callable = self.load()

                    ^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 57, in load

    return self.load_wsgiapp()

           ^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp

    return util.import_app(self.app_uri)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/util.py", line 370, in import_app

    mod = importlib.import_module(module)

          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module

    return _bootstrap._gcd_import(name[level:], package, level)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import

  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load

  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked

  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked

  File "<frozen importlib._bootstrap_external>", line 940, in exec_module

  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed

  File "/app/app.py", line 17, in <module>

    file_handler = RotatingFileHandler('logs/dangote_app.log', maxBytes=10240000, backupCount=5)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/logging/handlers.py", line 155, in __init__

    BaseRotatingHandler.__init__(self, filename, mode, encoding=encoding,

  File "/usr/local/lib/python3.11/logging/handlers.py", line 58, in __init__

    logging.FileHandler.__init__(self, filename, mode=mode,

  File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__

    StreamHandler.__init__(self, self._open())

                                 ^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open

    return open_func(self.baseFilename, self.mode,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PermissionError: [Errno 13] Permission denied: '/app/logs/dangote_app.log'

[2026-01-19 17:48:46 +0000] [7] [INFO] Worker exiting (pid: 7)

[2026-01-19 17:48:46 +0000] [8] [ERROR] Exception in worker process

Traceback (most recent call last):

  File "/usr/local/lib/python3.11/site-packages/gunicorn/arbiter.py", line 608, in spawn_worker

    worker.init_process()

  File "/usr/local/lib/python3.11/site-packages/gunicorn/workers/base.py", line 135, in init_process

    self.load_wsgi()

  File "/usr/local/lib/python3.11/site-packages/gunicorn/workers/base.py", line 147, in load_wsgi

    self.wsgi = self.app.wsgi()

                ^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/base.py", line 66, in wsgi

    self.callable = self.load()

                    ^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 57, in load

    return self.load_wsgiapp()

           ^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/app/wsgiapp.py", line 47, in load_wsgiapp

    return util.import_app(self.app_uri)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/site-packages/gunicorn/util.py", line 370, in import_app

    mod = importlib.import_module(module)

          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/importlib/__init__.py", line 126, in import_module

    return _bootstrap._gcd_import(name[level:], package, level)

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "<frozen importlib._bootstrap>", line 1204, in _gcd_import

  File "<frozen importlib._bootstrap>", line 1176, in _find_and_load

  File "<frozen importlib._bootstrap>", line 1147, in _find_and_load_unlocked

  File "<frozen importlib._bootstrap>", line 690, in _load_unlocked

  File "<frozen importlib._bootstrap_external>", line 940, in exec_module

  File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed

  File "/app/app.py", line 17, in <module>

    file_handler = RotatingFileHandler('logs/dangote_app.log', maxBytes=10240000, backupCount=5)

                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/logging/handlers.py", line 155, in __init__

    BaseRotatingHandler.__init__(self, filename, mode, encoding=encoding,

  File "/usr/local/lib/python3.11/logging/handlers.py", line 58, in __init__

    logging.FileHandler.__init__(self, filename, mode=mode,

  File "/usr/local/lib/python3.11/logging/__init__.py", line 1181, in __init__

    StreamHandler.__init__(self, self._open())

                                 ^^^^^^^^^^^^

  File "/usr/local/lib/python3.11/logging/__init__.py", line 1213, in _open

    return open_func(self.baseFilename, self.mode,

           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PermissionError: [Errno 13] Permission denied: '/app/logs/dangote_app.log'

[2026-01-19 17:48:46 +0000] [8] [INFO] Worker exiting (pid: 8)

[2026-01-19 17:48:46 +0000] [1] [ERROR] Worker (pid:6) exited with code 3

[2026-01-19 17:48:46 +0000] [1] [ERROR] Worker (pid:8) was sent SIGTERM!

[2026-01-19 17:48:46 +0000] [1] [ERROR] Worker (pid:7) was sent SIGTERM!

[2026-01-19 17:48:46 +0000] [1] [ERROR] Shutting down: Master

[2026-01-19 17:48:46 +0000] [1] [ERROR] Reason: Worker failed to boot.

