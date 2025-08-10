import threading
import os
from bot import main as bot_main
from admin_panel import app as panel_app

def run_bot():
    bot_main()

def run_panel():
    # Use port from env (Railway may set PORT), default 5000
    port = int(os.getenv('PORT', '5000'))
    panel_app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    t1 = threading.Thread(target=run_bot, daemon=True)
    t2 = threading.Thread(target=run_panel, daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
