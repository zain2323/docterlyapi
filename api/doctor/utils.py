from datetime import datetime

def get_experience(qualifications):
    # Returns the experience of the doctor by subracting the earliest date of degree procurement from the current date
    date_format = "%Y-%m-%d"
    min_date = str(min(qualifications["procurement_year"]))
    current_date = str(datetime.now().date())

    min_date = datetime.strptime(min_date, date_format)
    current_date = datetime.strptime(current_date, date_format)

    return int((abs(current_date - min_date).days)/365)