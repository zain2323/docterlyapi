from api import ma

class UserSchema(ma.Schema):
    id = ma.auto_field()  