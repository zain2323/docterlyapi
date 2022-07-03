from datetime import datetime
from pathlib import Path
import secrets
from PIL import Image

def get_experience(qualifications):
    # Returns the experience of the doctor by subracting the earliest date of degree procurement from the current date
    date_format = "%Y-%m-%d"
    min_date = str(min(qualifications["procurement_year"]))
    current_date = str(datetime.now().date())

    min_date = datetime.strptime(min_date, date_format)
    current_date = datetime.strptime(current_date, date_format)

    return int((abs(current_date - min_date).days)/365)

def save_picture(image_data, img_name):
    '''
    This saves the thumbnail picture of the product in the static/product_pictures directory.
    Picture is being renamed  to the randomly chosen 32 bit string in order to avoid the
    naming clash.
    '''
    try:
        path = Path('./api/static/doctor_profile_pics')
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

def delete_picture(img_name):
    try:
        path = Path("./api/static/doctor_profile_pics/" + img_name)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    if path.exists():
        path.unlink()


def generate_hex_name():
    '''
    Returns the 32 bit random digits
    '''
    return secrets.token_hex(32)