from app import db
from app.user_model.user_model import User


class Research:

    def __init__(self, user_id):
        self.user = User(user_id, user_id)
        self.gender_pref = self.get_gender_and_pref()
        self.match_ids = list()
        self.offers = list()
        for gender_pref_item in self.gender_pref:
            sql = '''SELECT id FROM users WHERE gender=(SELECT id FROM gender WHERE gender.type=%s)
                    AND preferences=(SELECT id FROM preferences WHERE preferences.type=%s)
                    AND id!=%s;'''
            cursor = db.cursor()
            cursor.execute(sql, (gender_pref_item['gender'], gender_pref_item['preferences'], self.user.id))
            self.match_ids += [item['id'] for item in cursor.fetchall()]
        for id in self.match_ids:
            self.offers.append(User(id, user_id))
        cursor.close()
    
    def get_gender_and_pref(self):
        gender_pref = list()
        if self.user.gender == 'male':
            if self.user.preferences == 'straight':
                gender_pref.append({'gender': 'female', 'preferences': 'straight'})
                gender_pref.append({'gender': 'female', 'preferences': 'bi-sexual'})
            elif self.user.preferences == 'homosexual':
                gender_pref.append({'gender': 'male', 'preferences': 'homosexual'})
                gender_pref.append({'gender': 'male', 'preferences': 'bi-sexual'})
            elif self.user.preferences == 'bi-sexual':
                gender_pref.append({'gender': 'female', 'preferences': 'straight'})
                gender_pref.append({'gender': 'female', 'preferences': 'bi-sexual'})
                gender_pref.append({'gender': 'male', 'preferences': 'homosexual'})
                gender_pref.append({'gender': 'male', 'preferences': 'bi-sexual'})
        elif self.user.gender == 'female':
            if self.user.preferences == 'straight':
                gender_pref.append({'gender': 'male', 'preferences': 'straight'})
                gender_pref.append({'gender': 'male', 'preferences': 'bi-sexual'})
            elif self.user.preferences == 'homosexual':
                gender_pref.append({'gender': 'female', 'preferences': 'homosexual'})
                gender_pref.append({'gender': 'female', 'preferences': 'bi-sexual'})
            elif self.user.preferences == 'bi-sexual':
                gender_pref.append({'gender': 'male', 'preferences': 'straight'})
                gender_pref.append({'gender': 'male', 'preferences': 'bi-sexual'})
                gender_pref.append({'gender': 'female', 'preferences': 'homosexual'})
                gender_pref.append({'gender': 'female', 'preferences': 'bi-sexual'})
        return gender_pref
        
    def sort(self, param='weight'):
        reverse = True
        if param == 'age' or param == 'distance':
            reverse = False
        self.offers.sort(key=lambda x: getattr(x, param), reverse=reverse)
    
    def filter(self, param='distance', value=100):
        if param == 'distance':
            self.offers = list(filter(lambda x: x.distance <= value, self.offers))
        elif param == 'age':
            self.offers = list(filter(lambda x: value[0] <= x.age <= value[1], self.offers))
        elif param == 'sexuality':
            self.offers = list(filter(lambda x: x.sexuality >= value, self.offers))
        elif param == 'common_interests_count':
            self.offers = list(filter(lambda x: x.common_interests_count > 0, self.offers))
        elif param == 'interests':
            lover_val = [val.lower() for val in value]
            self.offers = list(filter(lambda x: (len(set(x.interests_list) &
                            set(lover_val)) == len(set(lover_val))), self.offers))

    def get_users_per_page(self, page, per_page):
        self.offers = self.offers[(page * per_page - per_page):(page * per_page)]
