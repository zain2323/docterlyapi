from api import admin_manager as admin, db
from api.models import (User, Doctor, Qualification, Specialization, Day, Role, Rating,
                         Appointment, Slot, Patient, doctor_specializations)
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin.base import AdminIndexView

class RestrictedAccess(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.role_name == 'admin'
        
    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Please sign in to continue", 'info')
        return redirect(url_for('web_admin.sign_in'))

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        return redirect(url_for("web_admin.sign_out"))

class UserView(RestrictedAccess):
    can_create = False
    can_delete = False
    column_exclude_list = ['password', 'token', 'token_expiration']
    column_searchable_list = ['name', 'email']

class DoctorView(RestrictedAccess):
    can_create = False
    can_delete = False

class PatientView(RestrictedAccess):
    can_create = False
    can_delete = False

    column_exclude_list = [""]

class RoleView(RestrictedAccess):
    can_create = True
    can_edit = True
    can_delete = False

    form_excluded_columns = ['user']

class QualificationAndDoctorView(RestrictedAccess):
    can_create = True
    can_edit = True
    can_delete = True

    form_excluded_columns = ['doctor']

class DayView(RestrictedAccess):
    can_create = True
    can_edit = True
    can_delete = True

    form_excluded_columns = ['slot']

class RatingView(RestrictedAccess):
    can_delete = True   
    can_edit = False
    can_create = False

class AppointmentView(RestrictedAccess):
    can_edit = True
    can_delete = False
    can_create = False

    # column_searchable_list = ["date"]

class SlotView(RestrictedAccess):
    can_edit = True
    can_delete = False
    can_create = False

    column_searchable_list = ["day_id", "doctor_id"]

# class PrescribedMedicinesView(RestrictedAccess):
#     can_edit = False
#     can_delete = False
#     can_create = False

#     column_searchable_list = ["prescription_id", "medicine_name", "brand", "medicine_formula"]

admin.add_view(UserView(User, db.session))
admin.add_view(QualificationAndDoctorView(Qualification, db.session))
admin.add_view(QualificationAndDoctorView(Specialization, db.session))
admin.add_view(RoleView(Role, db.session))
admin.add_view(DayView(Day, db.session))
admin.add_view(RatingView(Rating, db.session))
admin.add_view(AppointmentView(Appointment, db.session))
admin.add_view(SlotView(Slot, db.session))
# admin.add_view(PrescribedMedicinesView(PrescribedMedicines, db.session))
admin.add_view(DoctorView(Doctor, db.session))
admin.add_view(PatientView(Patient, db.session))
admin.add_view(LogoutView(name="Logout", endpoint="logout"))