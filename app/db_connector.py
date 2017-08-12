from pymysql.connections import Connection
from pymysql import cursors


class Db(Connection):
    def __init__(self, app=None):
        if app is not None:
            self.connect_db(app)

    def connect_db(self, app):
        super(Db, self).__init__(host=app.config['SQL_HOST'],
                                user=app.config['SQL_USER'],
                                password=app.config['SQL_PASSWORD'],
                                db=app.config['SQL_DB'],
                                charset='utf8mb4',
                                cursorclass=cursors.DictCursor)
        sql = '''SET time_zone = '+3:00';'''
        cursor = self.cursor()
        cursor.execute(sql)
        self.commit()
        cursor.close()
