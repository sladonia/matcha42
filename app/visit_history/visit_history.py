from app import db


class VisitHistory:
    
    @staticmethod
    def add_item(user_id, other_user_id, other_user_login, url, msg_type):
        msgs = {
            'view': ' viewed your profile',
            'like': ' liked your profile',
            'dislike': ' broke the connection'
        }
        msg = msgs[msg_type]
        sql = '''INSERT INTO visit_history(user_id, other_user_id, other_user_login, url, msg)
                  VALUES(%s, %s, %s, %s, %s);'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, other_user_id, other_user_login, url, msg))
        db.commit()
        
    @staticmethod
    def get_visit_history(user_id, limit=30):
        sql = '''SELECT user_id, other_user_id, other_user_login, msg, url, DATE_FORMAT(date_time, %s)
                  AS date_str FROM visit_history WHERE user_id=%s ORDER BY date_time LIMIT %s;'''
        cursor = db.cursor()
        formater = "%b %D, %H:%i"
        cursor.execute(sql, (formater, user_id, limit))
        return cursor.fetchall()
