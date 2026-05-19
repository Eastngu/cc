import pymysql
pymysql.install_as_MySQLdb()  # PyMySQL drop-in for mysqlclient

from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
