from api.models import User
from api.user.schema import UserSchema
from datetime import datetime
user_schema = UserSchema()
user = '''{
    "name": "zain",
    "email": "zain@email.com",
    "password": "testing123",
    "dob": "2002-05-22",
    "gender": "male",
    "role_id": 1
}'''

loaded_user = user_schema.load(user)
print(loaded_user)

from api.models import *
from api.doctor.schema import *

doctor = Doctor.query.all()[-1]
ds = DoctorSchema()
print(ds.dump(doctor))