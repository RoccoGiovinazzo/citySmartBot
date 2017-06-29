web: gunicorn smartBot.wsgi --timeout 60 --keep-alive 5 --log-level debug
worker: python main.py --timeout 15 --keep-alive 5 --log-level debug