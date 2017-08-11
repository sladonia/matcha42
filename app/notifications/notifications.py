from app import db


class Notifications:
    
    def __init__(self, uid, other_login, url, settings, msg_type, other_id):
        notif_msgs = {
            'likes_me': 'User {0} liked your account',
            'unlikes_me': 'User {0} suspends your connection',
            'likes_me_back': 'Congratulations! You have a new connection with {0}',
            'viewed_my_profile': 'User {0} viewed your profile',
            'incoming_massage': 'You have got a new massage from {0}'
        }
        if settings.settings_list[msg_type] == 1:
            msg = notif_msgs[msg_type].format(other_login)
            Notifications.add(uid, msg, url, other_id, msg_type)
    
    @staticmethod
    def add(user_id, msg, url, other_id, msg_type):
        sql = "INSERT INTO notifications(msg, user_id, url, from_user, msg_type) VALUES(%s, %s, %s, %s, %s);"
        cursor = db.cursor()
        cursor.execute(sql, (msg, user_id, url, other_id, msg_type))
    
    @staticmethod
    def get_n(user_id, n=20):
        sql = '''SELECT msg, url, DATE_FORMAT(date_time, %s) AS date_time, seen FROM
              notifications WHERE user_id=%s ORDER BY date_time LIMIT %s;'''
        cursor = db.cursor()
        formater = '%d/%m/%Y %k:%i'
        cursor.execute(sql, (formater, user_id, n))
        l = cursor.fetchall()
        return l
    
    @staticmethod
    def get_unread(user_id):
        sql = '''SELECT msg, url, DATE_FORMAT(date_time, %s) AS date_time, seen
              FROM notifications WHERE user_id=%s AND seen=0 ORDER BY date_time;'''
        formater = '%d/%m/%Y %k:%i'
        cursor = db.cursor()
        cursor.execute(sql, (formater, user_id))
        l = cursor.fetchall()
        return l
    
    @staticmethod
    def set_as_read(user_id):
        sql = '''UPDATE notifications
              SET seen=1
              WHERE user_id=%s'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        db.commit()
    
    @staticmethod
    def count_unread(user_id):
        sql = '''SELECT COUNT(*) as quantity FROM notifications WHERE user_id=%s AND seen=0;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        return cursor.fetchone()['quantity']
    
    @staticmethod
    def update_last_seen(user_id):
        sql = '''UPDATE users
                SET last_seen=CURRENT_TIMESTAMP
                WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        db.commit()
        
    @staticmethod
    def viewed_profile_notification_allowed(user_id, watcher_id):
        sql = '''SELECT count(*) AS coun FROM notifications
                  WHERE user_id=%s AND from_user=%s AND seen=0 AND
                  msg_type="viewed_my_profile";'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, watcher_id))
        if cursor.fetchone()['coun'] == 0:
            return True
        return False
        


class NotificationSteeings:
    def __init__(self, uid):
        sql = '''SELECT * FROM notification_settings WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        result = cursor.fetchone()
        self.user_id = uid
        self.settings_list = dict()
        self.settings_list['likes_me'] = result['likes_me']
        self.settings_list['unlikes_me'] = result['unlikes_me']
        self.settings_list['likes_me_back'] = result['likes_me_back']
        self.settings_list['viewed_my_profile'] = result['viewed_my_profile']
        self.settings_list['incoming_massage'] = result['incoming_massage']
