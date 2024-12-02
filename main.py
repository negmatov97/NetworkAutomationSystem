import os
import threading
import time
import schedule
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from db_config import db, seed_data
from gen_token import api_bp as api_bp
from explator import user_api as user_api
from Ipv4_tab import frist_api
from default_date import default_api as default_api
from statistics import statis_api
from backup import backup
from device_conf import config as config
from LogView import logs as logs
from backup_auto.backuptestor import backup_function
from service import service as service
from flask_migrate import Migrate


load_dotenv()


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
CORS(app)


migrate = Migrate(app, db)

# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.yaml'


db.init_app(app)

# Register blueprints
app.register_blueprint(api_bp)
app.register_blueprint(user_api)
app.register_blueprint(frist_api)
app.register_blueprint(backup)
app.register_blueprint(config)
app.register_blueprint(logs)
app.register_blueprint(default_api)
app.register_blueprint(statis_api)
app.register_blueprint(service)

@app.cli.command("seed")
def seed():
    """Boshlang'ich ma'lumotlarni kiritadi."""
    seed_data()

# Backup-related functions and scheduling

def schedule_tasks():
    schedule.every().day.at("15:11").do(lambda: backup_function('1'))
    schedule.every().saturday.at("00:00").do(lambda: backup_function('7'))
    schedule.every(2).days.at("15:23").do(lambda: backup_function('2'))
    schedule.every(15).days.at("02:00").do(lambda: backup_function('15'))
    schedule.every(30).days.at("00:00").do(lambda: backup_function('30'))

    while True:
        schedule.run_pending()
        time.sleep(30)

# Start the scheduling in a separate thread
def start_scheduler():
    scheduler_thread = threading.Thread(target=schedule_tasks)
    scheduler_thread.daemon = True
    scheduler_thread.start()


if __name__ == "__main__":
    start_scheduler()
    host = 'localhost'
    port = 8080
    app.run(debug=True, host=host, port=port)
