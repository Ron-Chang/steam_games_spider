import redis
from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_dbpacemaker import DBPacemaker

app = Flask(__name__)

config = Config()
app.config.from_object(config)

db = SQLAlchemy(app)

from common.models import *

DBPacemaker.run(app, config=config, display=True)

spider_rs = redis.StrictRedis(
    host=config.SPIDER_REDIS_HOST,
    password=config.SPIDER_REDIS_PASSWORD,
    port=config.REDIS_PORT,
    charset='utf-8',
    decode_responses=True)

def create_app():
    return app
