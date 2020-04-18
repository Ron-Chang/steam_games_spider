import os


class Config:

    SECRET_KEY = os.environ['SECRET_KEY']

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DB_NAME = 'spider'

    USR = os.environ['SPIDER_MYSQL_USER']
    PWD = os.environ['SPIDER_MYSQL_PASSWORD']
    HOST = os.environ['SPIDER_MYSQL_HOST']
    PORT = os.environ['SPIDER_MYSQL_PORT']

    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/empty?charset=utf8mb4'

    SQLALCHEMY_BINDS = {
        DB_NAME: f'mysql+pymysql://{USR}:{PWD}@{HOST}:{PORT}/{DB_NAME}?charset=utf8mb4'
    }

    # for DBPacemaker - 透過定時排程請求DB，保持連線
    DB_PACEMAKER_SWITCH = True if os.environ['ENVIRONMENT'] == 'develop' else False
    MODELS_PATH_LIST = ['common.models']
    POKE_DB_INTERVAL = 60 * 60

    SPIDER_REDIS_HOST = os.environ['SPIDER_REDIS_HOST']
    SPIDER_REDIS_PASSWORD = os.environ.get('SPIDER_REDIS_PASSWORD')

    REDIS_PORT = os.environ['REDIS_PORT']

    ENVIRONMENT = os.environ['ENVIRONMENT']

    SYSTEM_NAME = 'steam_games_spider'
