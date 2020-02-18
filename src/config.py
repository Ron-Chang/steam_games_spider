import os


class Config:

    SECRET_KEY = os.environ['SECRET_KEY']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_NAME = 'spider'

    USR = os.environ['SPIDER_MYSQL_USER']
    PWD = os.environ['SPIDER_MYSQL_PASSWORD']
    HOST = os.environ['SPIDER_MYSQL_HOST']
    PORT = os.environ['SPIDER_MYSQL_PORT']

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/empty'

    SQLALCHEMY_BINDS = {
        DB_NAME: f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/{DB_NAME}'
    }

    SPIDER_REDIS_HOST = os.environ['SPIDER_REDIS_HOST']
    SPIDER_REDIS_PASSWORD = os.environ.get('SPIDER_REDIS_PASSWORD')

    REDIS_PORT = os.environ['REDIS_PORT']

    ENVIRONMENT = os.environ['ENVIRONMENT']

    SYSTEM_NAME = 'steam_games_spider'
