from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from flask import session, url_for, current_app
from datetime import datetime
from app import db
import socket
import re
import os
import shutil
import base64
from PIL import Image
from resizeimage import resizeimage
from io import BytesIO
from random import randint
import time
import math


class User:

    def __init__(self, user_id, this_user_id):
        self.id = user_id

        profile_settings = User.get_profile_settings_from_db(user_id)

        self.login = profile_settings['login']
        self.first_name = profile_settings['first_name']
        self.last_name = profile_settings['last_name']
        self.preferences = profile_settings['preferences']
        self.biography = profile_settings['biography']
        self.gender = profile_settings['gender']
        self.man_or_woman = profile_settings['gender_name']
        self.online_status = User.get_online_status(user_id)
        self.connection_ids, self.requested_connection_ids, self.unconfirmed_connection_ids = \
            User.get_all_connection_ids(user_id)
        self.homepage = url_for('routes.other_profile_view', login=self.login)
        self.avatar_path = User.get_avatar_path(user_id)
        self.sm_avatar_path = User.get_sm_avatar_path(user_id)
        self.age = profile_settings['age']
        self.sexuality = profile_settings['sexuality']
        self.city = profile_settings['city']
        self.lat, self.lon = User.get_lat_lon(user_id)
        self.interests_str = profile_settings['interests']
        self.interests_list = [interest.lower() for interest in User.get_interests_list(user_id)]
        self.connection_status = User.get_connection_status(this_user_id, user_id)
        self.connection_status_str = User.get_connection_status_str(self.connection_status, self.login)
        self.photos_paths = User.get_photos_path(user_id)
        self.unread_msgs = None
        self.distance = round(User.get_distance(user_id, this_user_id), 2)
        self.common_interests_count = User.get_count_common_interests(self.interests_list,
            [interest.lower() for interest in User.get_interests_list(this_user_id)])
        self.weight = User.get_weight(self.distance, self.sexuality, self.common_interests_count)
        self.is_blocked = User.is_blocked(self.id, this_user_id)

    @staticmethod
    def get_weight(distance, sexuality, common_interests_count):
        if distance is None:
            distance = 100
        elif distance == 0.0:
            distance = 1
        return 1 / distance + sexuality / 150 + common_interests_count / 3

    @staticmethod
    def get_count_common_interests(interests_list_1, interests_list_2):
        inter = set(interests_list_1) & set(interests_list_2)
        return len(inter)

    @staticmethod
    def get_lat_lon(uid):
        sql = '''SELECT lat, lon FROM geolocation WHERE user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        result = cursor.fetchone()
        if result is not None:
            return result['lat'], result['lon']
        return None, None

    @staticmethod
    def get_username(uid):
        sql = '''SELECT login FROM users WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        result = cursor.fetchone()
        if result is not None:
            return result['login']
        return None

    @staticmethod
    def get_user_id(login):
        sql = "SELECT id FROM users WHERE login=%s;"
        cursor = db.cursor()
        cursor.execute(sql, login)
        result = cursor.fetchone()
        if result is not None:
            return result['id']
        return None

    @staticmethod
    def register(login, email, passwd, first_name, last_name, date_of_birth):
        hashed_passwd = generate_password_hash(passwd)
        date1 = datetime.strptime(date_of_birth, '%d/%m/%Y').strftime('%Y/%m/%d')
        sql = '''INSERT INTO users(`login`, `email`, `passwd`, `first_name`, `last_name`, `date_of_birth`) VALUES (%s, %s, %s, %s, %s, %s);'''
        cursor = db.cursor()
        cursor.execute(sql, (login, email, hashed_passwd, first_name, last_name, date1))
        db.commit()
        sql = '''SELECT id from users WHERE login=%s;'''
        cursor.execute(sql, login)
        user_id = cursor.fetchone()['id']
        sql = "INSERT INTO notification_settings(user_id) VALUES(%s);"
        cursor.execute(sql, user_id)
        db.commit()
        User.update_geolocation(user_id, 50.0, 30.0)


    @staticmethod
    def remove_user(login):
        sql = 'DELETE FROM users WHERE login=%s;'
        db.cursor().execute(sql, (login,))
        db.commit()
        User.delete_user_folder(login)

    @staticmethod
    def verify_passwd(login, passwd):
        sql = "SELECT passwd FROM users WHERE login=%s;"
        cursor = db.cursor()
        cursor.execute(sql, (login,))
        result = cursor.fetchone()
        if (result):
            hashed_passwd = result['passwd']
            return check_password_hash(hashed_passwd, passwd)
        else:
            return False

    @staticmethod
    def login_exists(login):
        sql = "SELECT COUNT(*) FROM users WHERE login=%s;"
        cursor = db.cursor()
        cursor.execute(sql, (login))
        result = cursor.fetchone()
        if result['COUNT(*)'] == 0:
            return False
        else:
            return True

    @staticmethod
    def email_exists(email):
        sql = "SELECT COUNT(*) FROM users WHERE email=%s;"
        cursor = db.cursor()
        cursor.execute(sql, (email))
        result = cursor.fetchone()
        if result['COUNT(*)'] == 0:
            return False
        else:
            return True

    @staticmethod
    def log_in(login):
        sql = "SELECT id FROM users WHERE login=%s;"
        cursor = db.cursor()
        cursor.execute(sql, (login))
        result = cursor.fetchone()
        session['id'] = result['id']
        session['login'] = login

    @staticmethod
    def log_out():
        del session['id']
        del session['login']

    @staticmethod
    def verify_user_session():
        if 'login' in session and 'id' in session:
            sql = "SELECT * FROM users WHERE login=%s AND id=%s;"
            cursor = db.cursor()
            cursor.execute(sql, (session['login'], session['id']))
            if cursor.fetchone() is not None:
                return True
        return False

    @staticmethod
    def auth():
        if User.verify_user_session():
            sql = "SELECT activated from users WHERE login=%s AND id=%s;"
            cursor = db.cursor()
            cursor.execute(sql, (session['login'], session['id'],))
            activated = cursor.fetchone()['activated']
#            print(activated)
            return activated
        return 0

    @staticmethod
    def accept_confirmation_email(login):
        if User.login_exists(login):
            sql = "SELECT activated from users WHERE login=%s;"
            cursor = db.cursor()
            cursor.execute(sql, login)
            activated = cursor.fetchone()
            if activated['activated'] <= 1:
                return True
            else:
                return False
        else:
            return False

    @staticmethod
    def update_access_status(login, n):
        cursor = db.cursor()
        sql = "UPDATE users SET activated=%s WHERE login=%s;"
        cursor.execute(sql, (n, login))
        db.commit()

    @staticmethod
    def send_email(to, subject, msg):
        # gmail_sender = 'ladonya.s@gmail.com'
        gmail_sender = 'matchafortytwo@gmail.com'
        # gmail_passwd = environ.get('G_PASSWD')
        gmail_passwd = '1234567q'
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)
        BODY = '\r\n'.join(['To: %s' % to, 'From: %s' % gmail_sender, 'Subject: %s' % subject, '', msg])
        try:
            server.sendmail(gmail_sender, [to], BODY)
            # print('email sent')
        except:
            print('error sending mail')
        server.quit()

    @staticmethod
    def send_reset_passwd_email(email):
        sql = '''SELECT id, login FROM users WHERE email=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, email)
        result = cursor.fetchone()
        id = result['id']
        login = result['login']
        token = randint(1, 2147483647)
        sql = '''UPDATE users
                  SET token=%s
                 WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (token, id))
        db.commit()
        msg = 'Follow the link to reset password for {0}: \n{1}'
        msg = msg.format(login, url_for('routes.assign_new_passwd_view',
                                        login=login, token=token, _external=True))
        subject = 'Reset password. Matcha'
        User.send_email(email, subject, msg)


    @staticmethod
    def check_login_token(login, token):
        sql = '''SELECT token FROM users WHERE login=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, login)
        result = cursor.fetchone()
        if result is None:
            return False
        if result['token'] == int(token):
            return True
        return False


    @staticmethod
    def send_registration_email(receiver, login):
        msg = 'Please follow the next link to continue registration:\n'
        msg += url_for('routes.create_profile_view', login=login, _external=True)
        print(msg)
        User.send_email(receiver, 'Registration. Matcha', msg)

    @staticmethod
    def get_gender_id(type):
        sql = "SELECT id FROM gender WHERE type=%s;"
        cursor = db.cursor()
        cursor.execute(sql, type)
        result = cursor.fetchone()
        if result is None:
            return 0
        else:
            return result['id']

    @staticmethod
    def get_preferences_id(type):
        sql = "SELECT id FROM preferences WHERE type=%s;"
        cursor = db.cursor()
        cursor.execute(sql, type)
        result = cursor.fetchone()
        if result is None:
            return 0
        else:
            return result['id']

    @staticmethod
    def get_interests_from_user(interests_str):
        my_regex = re.compile('(#[\w]+)')
        return my_regex.findall(interests_str)

    @staticmethod
    def get_interests_list(user_id):
        sql = "SELECT interest FROM interests WHERE user_id=%s"
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        interests_list = [x['interest'] for x in cursor.fetchall()]
        return interests_list

    @staticmethod
    def interests_to_db(user_id, interests_list):
        cursor = db.cursor()
        for interest in interests_list:
            sql = "INSERT INTO interests(user_id, interest) VALUES(%s, %s)"
            cursor.execute(sql, (user_id, interest))
            db.commit()

    @staticmethod
    def create_profile(user_id, gender, preferences, biography, interests, city, show_location):
        if show_location is False:
            s_l = 0
        else:
            s_l = 1
        sql = '''UPDATE users
                SET gender=(SELECT id FROM gender WHERE gender.type=%s),
                preferences=(SELECT id FROM preferences WHERE type=%s),
                biography=%s,
                city=%s,
                show_location=%s
                WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (gender, preferences, biography, city, s_l, user_id))
        db.commit()
        User.interests_to_db(user_id, User.get_interests_from_user(interests))

    @staticmethod
    def create_user_folder(username, user_id):
        os.mkdir(current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/' + username, 0o0755)
        shutil.copyfile(current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/av_mid.PNG',
                        current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/' + username + '/av_mid.PNG')
        shutil.copyfile(current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/av_min.PNG',
                        current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/' + username + '/av_min.PNG')
        User.add_photo_to_db(user_id, 0, '/static/photos/' + username + '/av_mid.PNG', 1)
        User.add_photo_to_db(user_id, 0, '/static/photos/' + username + '/av_min.PNG', 2)

    @staticmethod
    def delete_user_folder(username):
        shutil.rmtree(current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/' + username, True)

    @staticmethod
    def save_photos(key, image_string, user_id):
        img_path = '/static/photos/' + session['login'] + '/' + key
        im = Image.open(BytesIO(base64.b64decode(image_string)))
        img_save_path = current_app.config['ROOT_DIRECTORY'] + '/app' + img_path + '.' + im.format
        img_static_path = img_path + '.' + im.format
        im.save(img_save_path, im.format)
        sql = "INSERT INTO photos(user_id, photo_id, path) VALUES(%s, %s, %s);"
        cursor = db.cursor()
        cursor.execute(sql, (user_id, key, img_static_path))
        db.commit()

    @staticmethod
    def add_photo_to_db(user_id, photo_id, path, avatar):
        sql = "INSERT INTO photos(user_id, photo_id, path, avatar) VALUES(%s, %s, %s, %s);"
        cursor = db.cursor()
        cursor.execute(sql, (user_id, photo_id, path, avatar))
        db.commit()

    @staticmethod
    def update_avatar_photo_to_db(user_id, photo_id, path, avatar):
        sql = '''UPDATE photos
                  SET  photo_id=%s, path=%s
                  WHERE user_id=%s AND avatar=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (photo_id, path, user_id, avatar))
        db.commit()

    @staticmethod
    def get_photo_id_for_debug(uid):
        sql ='''SELECT photo_id from photos WHERE user_id=%s AND avatar=0;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        result = cursor.fetchone()
        if result is None:
            return None
        return result['photo_id']


    @staticmethod
    def set_avatar(avatar_photo_id, user_id, login):
        sql = '''SELECT path FROM photos WHERE user_id=%s AND photo_id=%s AND avatar=0;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, avatar_photo_id))
        result = cursor.fetchone()
        if result is not None:
            avatar_static_origin = result['path']
        else:
            avatar_static_origin = '/static/photos/default_profile.png'
            User.update_access_status(login, 2)
        size_sm = 60, 60
        size_mid = 300, 350
        common_path = '/static/photos/'
        user_folder_path = common_path + login + '/'
        im = Image.open(current_app.config['ROOT_DIRECTORY'] + '/app' + avatar_static_origin)

        covered_sm = resizeimage.resize_cover(im, size_sm, validate=False)
        covered_mid = resizeimage.resize_cover(im, size_mid, validate=False)

        covered_sm_static_path = user_folder_path + 'av' + str(time.time()) + '_min.' + im.format
        covered_mid_static_path = user_folder_path + 'av' + str(time.time()) + '_mid.' + im.format

        covered_sm.save(current_app.config['ROOT_DIRECTORY'] + '/app' + covered_sm_static_path, im.format, quality=100)
        covered_mid.save(current_app.config['ROOT_DIRECTORY'] + '/app' + covered_mid_static_path, im.format, quality=100)

        # delete old avatars
        sql = '''SELECT path FROM photos WHERE user_id=%s AND (avatar=1 OR avatar=2);'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        result = cursor.fetchall()
        for item in result:
            os.remove(current_app.config['ROOT_DIRECTORY'] + '/app' + item['path'])

        User.update_avatar_photo_to_db(user_id, 0, covered_sm_static_path, 2)
        User.update_avatar_photo_to_db(user_id, 0, covered_mid_static_path, 1)

    @staticmethod
    def delete_photo(photo_id, user_id):
        cursor = db.cursor()
        sql = "SELECT path FROM photos WHERE user_id=%s AND photo_id=%s;"
        cursor.execute(sql, (user_id, photo_id))
        static_path = cursor.fetchone()['path']
        path = current_app.config['ROOT_DIRECTORY'] + '/app' + static_path
        os.remove(path)
        sql = '''DELETE FROM photos WHERE user_id=%s AND photo_id=%s;'''
        cursor.execute(sql, (user_id, photo_id))
        db.commit()

    @staticmethod
    def get_avatar_path(user_id):
        sql = '''SELECT path FROM photos WHERE user_id=%s AND avatar=1;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id))
        resust = cursor.fetchone()
        if resust is not None:
            return resust['path']
        return '/static/photos/default_profile.png'

    @staticmethod
    def get_sm_avatar_path(user_id):
        sql = '''SELECT path FROM photos WHERE user_id=%s AND avatar=2;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        resust = cursor.fetchone()
        if resust is not None:
            return resust['path']
        return '/static/photos/default_profile.png'

    @staticmethod
    def get_avatar_mini_path(user_id):
        sql = '''SELECT path FROM photos WHERE user_id=%s AND avatar=2;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id))
        resust = cursor.fetchone()
        if resust is not None:
            return resust['path']
        return '/static/photos/default_profile.png'

    @staticmethod
    def get_photos_path(user_id):
        sql = '''SELECT path FROM photos WHERE user_id=%s AND avatar=0;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id))
        resust = cursor.fetchall()
        if resust is not None:
            return [item['path'] for item in resust]
        return None

    @staticmethod
    def get_profile_settings_from_db(user_id):
        sql = '''SELECT users.login, users.email, users.first_name, users.last_name, users.sexuality,
        DATE_FORMAT(users.date_of_birth, %s) AS date_of_birth, gender.type AS gender,
        preferences.type AS preferences, users.biography,
        users.city, users.show_location
        FROM users, gender, preferences
        WHERE users.preferences=preferences.id AND users.gender=gender.id AND users.id=%s;
        '''
        cursor = db.cursor()
        date_formater = "%d/%m/%Y"
        cursor.execute(sql, (date_formater, user_id,))
        result = cursor.fetchone()
        interests_list = User.get_interests_list(user_id)
        interests_str = ', '.join(interests_list)
        result['interests'] = interests_str
        result['age'] = User.get_age(result['date_of_birth'])
        result['gender_name'] = User.get_man_or_woman(result['gender'])
        return result

    @staticmethod
    def fill_edit_profile_form_from_db(form, user_id):
        result = User.get_profile_settings_from_db(user_id)
        form.login.data = result['login']
        form.email.data = result['email']
        form.first_name.data = result['first_name']
        form.last_name.data = result['last_name']
        form.birth_date.data = result['date_of_birth']
        form.gender.data = result['gender']
        form.preferences.data = result['preferences']
        form.biography.data = result['biography']
        form.interests.data = result['interests']
        form.city.data = result['city']
        form.show_location.data = True if result['show_location'] is 1 else False

    @staticmethod
    def get_email(user_id):
        sql = "SELECT email FROM users WHERE id=%s;"
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        result = cursor.fetchone()
        return result['email']

    @staticmethod
    def update_profile(user_id, login, first_name, last_name, date_of_birth, gender, preferences, biography, city, show_location):
        date1 = datetime.strptime(date_of_birth, '%d/%m/%Y').strftime('%Y/%m/%d')
        sql = '''UPDATE users
                  SET  login=%s, first_name=%s, last_name=%s,
                  date_of_birth=%s,
                  gender=(SELECT id FROM gender WHERE gender.type=%s),
                  preferences=(SELECT id FROM preferences WHERE preferences.type=%s),
                  biography=%s, city=%s, show_location=%s
                  WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (login, first_name, last_name, date1, gender, preferences, biography, city, show_location, user_id))
        db.commit()

    @staticmethod
    def update_passwd(user_id, passwd):
        hashed_passwd = generate_password_hash(passwd)
        sql = '''UPDATE users
                SET passwd=%s
                WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (hashed_passwd, user_id))
        db.commit()

    @staticmethod
    def send_update_email_rwquest(receiver, login, user_id):
        sql = '''UPDATE users
                  SET users.new_email=%s
                  WHERE users.id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (receiver, user_id))
        db.commit()
        msg = 'Please follow the next link to confirm updated email:\n'
        ip = socket.gethostbyname(socket.gethostname())
        msg += 'http://' + ip + ':5000' + url_for('routes.update_email_view', login=login)
        User.send_email(receiver, 'Matcha emil update', msg)


    @staticmethod
    def accept_update_email(login):
        sql = '''SELECT new_email FROM
                users WHERE login=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (login))
        result = cursor.fetchone()['new_email']
        if result is not None:
            return True
        return False

    @staticmethod
    def update_email(login):
        sql = '''SELECT new_email FROM users WHERE login=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, login)
        new_email = cursor.fetchone()['new_email']
        sql = '''UPDATE users
                  SET email=%s
                  WHERE users.login=%s;
                  UPDATE users
                  SET users.new_email=NULL
                  WHERE users.login=%s;'''
        cursor.execute(sql, (new_email, login, login))
        db.commit()

    @staticmethod
    def delete_interests(user_id):
        sql = "DELETE FROM interests WHERE interests.user_id=%s;"
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        db.commit()

    @staticmethod
    def update_interesrs(user_id, interests_str):
        User.delete_interests(user_id)
        interests_list = User.get_interests_from_user(interests_str)
        User.interests_to_db(user_id, interests_list)

    @staticmethod
    def update_notifications_settings(user_id, likes_me, unlikes_me, likes_me_back, viewed_my_profile, incoming_massage):
        sql = '''UPDATE notification_settings
                  SET likes_me=%s,
                  unlikes_me=%s,
                  likes_me_back=%s,
                  viewed_my_profile=%s,
                  incoming_massage=%s
                  WHERE user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (likes_me, unlikes_me, likes_me_back, viewed_my_profile, incoming_massage, user_id))
        db.commit()

    @staticmethod
    def get_notification_settings(user_id):
        sql = "SELECT * FROM notification_settings WHERE user_id=%s;"
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        return cursor.fetchone()

    @staticmethod
    def grep_image_number(img_filename):
        my_regex = re.compile('([0-9]+)')
        result = my_regex.search(img_filename)
        if result is not None:
            return result.group()
        return None

    @staticmethod
    def get_age(date_of_birth):
        date = datetime.strptime(date_of_birth, '%d/%m/%Y')
        today = datetime.now()
        return today.year - date.year - ((today.month, today.day) < (date.month, date.day))

    @staticmethod
    def get_man_or_woman(gender):
        if gender == 'male':
            return 'man'
        elif gender == 'female':
            return 'woman'
        else:
            return None

    # 0 - not connected
    # 1 - this_uid requested
    # 2 - other_uid requested
    # 3 - connected
    @staticmethod
    def get_connection_status(this_uid, other_uid):
        sql = '''SELECT * FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (this_uid, other_uid))
        result1 = cursor.fetchone()
        sql = '''SELECT * FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (other_uid, this_uid))
        result2 = cursor.fetchone()
        if result1 is None and result2 is None:
            return 0
        elif result1 is not None and result2 is not None:
            return 3
        elif result2 is not None:
            return 2
        elif result1 is not None:
            return 1

    @staticmethod
    def get_connection_status_str(status, login):
        CONNECTION_STATUS = ['You are not connected with {0}',
                             'You liked {0} profile',
                             '{0} liked your profile',
                             'You are connected with {0}']
        return CONNECTION_STATUS[status].format(login)

    @staticmethod
    def set_connection(this_uid, other_uid):
        sql = '''INSERT IGNORE INTO connections(this_uid, other_uid)  VALUES(%s, %s);'''
        cursor = db.cursor()
        cursor.execute(sql, (this_uid, other_uid))
        db.commit()

    @staticmethod
    def unset_connection(this_uid, other_uid):
        sql = '''DELETE IGNORE FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (this_uid, other_uid))
        db.commit()

    @staticmethod
    def connected(uid_1, uid_2):
        sql = '''SELECT COUNT(*) AS cou FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (uid_1, uid_2))
        first = cursor.fetchone()['cou']
        sql = '''SELECT COUNT(*) AS cou FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (uid_2, uid_1))
        second = cursor.fetchone()['cou']
        if first == 1 and second == 1:
            return True
        return False

    @staticmethod
    def connection_requested(uid_1, uid_2):
        sql = '''SELECT COUNT(*) AS cou FROM connections WHERE this_uid=%s AND other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (uid_1, uid_2))
        first = cursor.fetchone()['cou']
        if first == 1:
            return True
        return False


    # return:
    # confirmed
    # requested (by this)
    # unconfirmed (by this)
    @staticmethod
    def get_all_connection_ids(uid):
        sql = '''SELECT other_uid from connections WHERE this_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        my = cursor.fetchall()
        my_connections = [m['other_uid'] for m in my]

        sql = '''SELECT this_uid from connections WHERE other_uid=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, uid)
        other = cursor.fetchall()
        other_connections = [m['this_uid'] for m in other]

        confirmed_connections = list(set(my_connections).intersection(other_connections))
        requested_connections = list(set(my_connections) - set(other_connections))
        unconfirmed_connections = list(set(other_connections) - set(my_connections))

        return confirmed_connections, requested_connections, unconfirmed_connections

    @staticmethod
    def get_all_connections(connections_ids, this_user_id):
        connections = list()
        for id in connections_ids:
            connections.append(User(id, this_user_id))
        return connections

    @staticmethod
    def get_online_status(uid):
        sql = '''SELECT UNIX_TIMESTAMP(last_seen) AS time_stamp,
              DATE_FORMAT(last_seen, %s) AS date_str
              FROM users WHERE id=%s;'''
        cursor = db.cursor()
        formater = "%b %D, %H:%i"
        cursor.execute(sql, (formater, uid))
        result = cursor.fetchone()
        current_timestamp = int(time.time())
        if (current_timestamp - result['time_stamp']) <= 5:
            return 'Online'
        else:
            return 'Last seen: ' + result['date_str']

    @staticmethod
    def add_bot(login, id, photo_name, gender, first_name, last_name, date_of_birth, preferences, interests):
        User.register(login, 'dony.s@gml.com', '1234567q', first_name, last_name, date_of_birth)
        User.update_access_status(login, 2)
        User.create_profile(User.get_user_id(login), gender,
                            preferences,
                            'no lifew',
                            interests,
                            'kiev',
                            True)
        User.create_user_folder(login, id)
        shutil.copyfile(current_app.config['ROOT_DIRECTORY'] + '/app/static/img/' + photo_name,
                        current_app.config['ROOT_DIRECTORY'] + '/app/static/photos/' + login + '/1.jpg')
        User.add_photo_to_db(id, 1, '/static/photos/' + login + '/1.jpg', 0)
        avatar_id = User.get_photo_id_for_debug(2)
        User.set_avatar(avatar_id, id, login)
        User.update_access_status(login, 3)

    @staticmethod
    def update_sexuality(user_id, increment):
        sql = '''SELECT sexuality from users WHERE id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        sexuality = cursor.fetchone()['sexuality']
        if sexuality + increment >= 100:
            sexuality = 100
        elif sexuality + increment <= 0:
            sexuality = 100
        else:
            sexuality += increment
        sql = '''UPDATE users
                  SET sexuality = %s
                  WHERE id=%s;'''
        cursor.execute(sql, (sexuality, user_id))
        db.commit()

    @staticmethod
    def update_geolocation(user_id, lat, lon):
        sql = '''INSERT INTO geolocation(user_id, lat, lon)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE user_id=%s, lat=%s, lon=%s;
        '''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, lat, lon, user_id, lat, lon))
        db.commit()

    @staticmethod
    def get_geolocation(user_id):
        sql = "SELECT lat, lon FROM geolocation WHERE user_id=%s;"
        cursor = db.cursor()
        cursor.execute(sql, (user_id,))
        return cursor.fetchone()

    @staticmethod
    def get_distance(uid_1, uid_2):
        result = None
        l1 = User.get_geolocation(uid_1)
        l2 = User.get_geolocation(uid_2)
        if l1 is not None and l2 is not None:
            lat1, lon1, lat2, lon2 = map(math.radians, [l1['lat'], l1['lon'], l2['lat'], l2['lon']])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371
            result = c * r
        return result

    @staticmethod
    def get_all_lat_lng_login(user_id):
        sql = '''SELECT geolocation.lat, geolocation.lon AS lng, users.login FROM
                 geolocation, users WHERE users.id=geolocation.user_id AND
                 users.show_location=1 AND users.id!=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        return cursor.fetchall()

    @staticmethod
    def report_fake_account(user_id, fake_account_id):
        sql = '''INSERT INTO fake_accounts(user_id, fake_account_id) VALUES(%s, %s);'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, fake_account_id))
        db.commit()

    @staticmethod
    def block_user(user_id, blocked_user_id):
        sql = '''INSERT INTO blocked_users(user_id, blocked_user_id) VALUES(%s, %s)
                 ON DUPLICATE KEY UPDATE user_id=%s, blocked_user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, blocked_user_id, user_id, blocked_user_id))
        db.commit()
        User.unset_connection(user_id, blocked_user_id)

    @staticmethod
    def unblock_user(user_id, blocked_user_id):
        sql = '''DELETE FROM blocked_users WHERE user_id=%s AND blocked_user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (user_id, blocked_user_id))
        db.commit()

    @staticmethod
    def is_blocked(blocked_user_id, user_id):
        sql = '''SELECT COUNT(*) as coun FROM blocked_users WHERE blocked_user_id=%s AND user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, (blocked_user_id, user_id))
        result = cursor.fetchone()['coun']
        if result > 0:
            return True
        return False

    @staticmethod
    def get_all_blocked_ids(user_id):
        sql = '''SELECT blocked_user_id FROM blocked_users WHERE user_id=%s;'''
        cursor = db.cursor()
        cursor.execute(sql, user_id)
        result = cursor.fetchall()
        if result.__len__() == 0:
            return []
        return [id['blocked_user_id'] for id in result]
