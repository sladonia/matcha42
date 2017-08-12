from app import db


class Chat:
    def __init__(self, uid, connections):
        self.chat_dict = None
    
    @staticmethod
    def add(user_id, receiver_id, msg):
        sql = '''INSERT INTO chat(user_id, receiver_id, msg) VALUES(%s, %s, %s);'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, receiver_id, msg))
        db.commit()
        cursor.close()
    
    @staticmethod
    def get_all(user_1, user_2, limit=20):
        sql = '''SELECT msg, user_id, receiver_id, DATE_FORMAT(date_time, %s) AS date_time, seen
        FROM chat WHERE (user_id=%s AND receiver_id=%s) OR (user_id=%s AND receiver_id=%s)
        ORDER BY date_time;'''
        formater = "%b %D, %H:%i"
        cursor = db.cursor()
        cursor.execute(sql, (formater, user_1, user_2, user_2, user_1))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    @staticmethod
    def set_as_read(receiver_id, other_user_id):
        sql = '''UPDATE chat
              SET seen=1
              WHERE receiver_id=%s AND user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (receiver_id, other_user_id))
        db.commit()
        cursor.close()
    
    @staticmethod
    def get_unread(receiver_id, other_user_id):
        sql = '''SELECT msg, user_id, receiver_id, DATE_FORMAT(date_time, %s) AS date_time, seen
                FROM chat WHERE receiver_id=%s AND user_id=%s AND seen=0
                ORDER BY date_time;'''
        formater = "%b %D, %H:%i"
        cursor = db.cursor()
        cursor.execute(sql, (formater, receiver_id, other_user_id))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    @staticmethod
    def count_unread(receiver_id):
        sql = '''SELECT COUNT(*) AS quantity FROM chat WHERE receiver_id=%s AND seen=0;'''
        cursor = db.cursor()
        cursor.execute(sql, receiver_id)
        result = cursor.fetchone()['quantity']
        cursor.close()
        return result
    
    @staticmethod
    def get_count_from(receiver_id):
        sql = '''SELECT COUNT(*) AS quantity, user_id AS from_user FROM chat WHERE receiver_id=%s AND seen=0 GROUP BY user_id;'''
        cursor = db.cursor()
        cursor.execute(sql, receiver_id)
        result = cursor.fetchall()
        cursor.close()
        return result
    
    @staticmethod
    def get_count_unread_from(sender_id, receiver_id):
        sql = '''SELECT COUNT(*) AS number FROM chat
                WHERE user_id=%s AND receiver_id=%s AND seen=0;'''
        cursor = db.cursor()
        cursor.execute(sql, (sender_id, receiver_id))
        result = cursor.fetchone()['number']
        cursor.close()
        return result
    
    @staticmethod
    def get_user_by_id(user_1, user_2, id):
        if id == user_1.id:
            return user_1
        else:
            return user_2

    @staticmethod
    def chat_notification_allowed(receiver_id, sender_id):
        sql = '''SELECT count(*) AS coun FROM chat WHERE receiver_id=%s AND user_id=%s AND seen=0;'''
        cursor = db.cursor()
        cursor.execute(sql, (receiver_id, sender_id))
        result = cursor.fetchone()
        sql = '''SELECT count(*) AS coun FROM notifications WHERE user_id=%s AND from_user=%s AND seen=0 AND msg_type="incoming_massage";'''
        cursor = db.cursor()
        cursor.execute(sql, (receiver_id, sender_id))
        count_same = cursor.fetchone()['coun']
        cursor.close()
        if result['coun'] > 0 and count_same == 0:
            return True
        return False
