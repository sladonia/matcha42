from app import db
import math


class Geolocation:
    
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
        l1 = Geolocation.get_geolocation(uid_1)
        l2 = Geolocation.get_geolocation(uid_2)
        if l1 is not None and l2 is not None:
            lat1, lon1, lat2, lon2 = map(math.radians, [l1['lat'], l1['lon'], l2['lat'], l2['lon']])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371
            result = c * r
        return result
