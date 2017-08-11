from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, IntegerField, BooleanField, ValidationError
import re


class FilterForm(FlaskForm):
    order_by = SelectField(choices=[('weight', 'best match'), ('distance', 'distance'),
                                    ('sexuality', 'sexuality'), ('common_interests_count', 'common interests'),
                                    ('age', 'age')])
    distance = FloatField('distance', )
    sexuality = FloatField('sexuality')
    common_interests = StringField('common_interests')
    age_from = IntegerField('age_from')
    age_to = IntegerField('age_to')
    
    enable_distance = BooleanField('enable_distance')
    enable_sexuality = BooleanField('enable_sexuality')
    enable_interests = BooleanField('enable_interests')
    enable_age = BooleanField('enable_age')
    
    def validate_common_interests(self, field):
        if field.data != '':
            if re.fullmatch('.*(#[\w]+).*', field.data) is None:
                raise ValidationError('Interests tags should begin with #')
