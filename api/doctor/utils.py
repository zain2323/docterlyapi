from datetime import datetime
from pathlib import Path
import secrets
from PIL import Image
from api import db

def get_experience(qualifications):
    # Returns the experience of the doctor by subracting the earliest date of degree procurement from the current date
    date_format = "%Y-%m-%d"
    try:
        min_date = str(min(qualifications["procurement_year"]))
    except:
        min_date = str(datetime.now().date())
    current_date = str(datetime.now().date())

    min_date = datetime.strptime(min_date, date_format)
    current_date = datetime.strptime(current_date, date_format)

    return int((abs(current_date - min_date).days)/365)

def save_picture(image_data, img_name, loc='./api/static/doctor_profile_pics'):
    '''
    This saves the thumbnail picture of the product in the static/product_pictures directory.
    Picture is being renamed  to the randomly chosen 32 bit string in order to avoid the
    naming clash.
    '''
    try:
        path = Path(loc)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    try:
        _, ext = image_data.filename.split(".")
    except:
        ext = image_data.filename.split(".")[-1]
    image_name_with_ext = img_name + "." + ext
    path = path.joinpath(image_name_with_ext)
    try:
        i = Image.open(image_data)
    except FileNotFoundError:
        raise Exception(f"File {image_data} not found at the given path.")
    i = i.resize((500,375))
    i.save(path)
    return image_name_with_ext

def delete_picture(img_name, loc="./api/static/doctor_profile_pics/"):
    try:
        path = Path(loc + img_name)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    if path.exists():
        path.unlink()

def generate_hex_name():
    '''
    Returns the 32 bit random digits
    '''
    return secrets.token_hex(32)

def get_patient_count(doctor):
    id = doctor.id
    query = f"""SELECT COUNT(*) FROM doctor d
JOIN "user" u
ON u.id = d.user_id
JOIN slot s
ON s.doctor_id = d.id
JOIN appointment a
On a.slot_id = s.id
WHERE d.id = {id};"""
    return db.session.execute(query).all()[0][0]
    