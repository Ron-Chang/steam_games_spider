from core import models
from datetime import datetime
from app import create_app
from scraping_tools.backup_database import BackupDatabase


app = create_app()


if __name__ == '__main__':

    now = datetime.now()

    backup_dir = 'backup'

    BackupDatabase(models=models, now=now, backup_dir=backup_dir)
