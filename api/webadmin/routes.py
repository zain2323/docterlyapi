from flask import Blueprint, redirect, render_template, url_for, flash, request
from flask_login.utils import current_user, login_user, logout_user
from api.models import Role, User
from api import db
from api.webadmin.forms import SignUpForm, SignInForm
from datetime import datetime
from api.webadmin import web_admin

@web_admin.route("/signup", methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        name = form.name.data.lower()
        email = form.email.data.lower()
        password = form.password
        user_role = "user"
        if email == 'admin@admin.com':
            user_role = 'admin'
        role = Role.query.filter_by(role=user_role).first()
        if role is None:
            role = Role(role=user_role)
            db.session.add(role)
            db.session.commit()
        user = User(name=name, email=email, password=password, role_id=role.id, confirmed=True, dob=datetime.utcnow(), gender="male")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created successfully! You can now login.", 'success')
        return redirect(url_for('web_admin.sign_in'))
    return render_template("auth/signUp.html", title='Register', form=form)

@web_admin.route("/")
@web_admin.route("/signin", methods=['GET', 'POST'])
def sign_in():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if user.role.role == "admin" and not user.confirmed:
                user.confirmed = True
                db.session.commit()
            if not user.confirmed:
                flash("Confirmation email has been sent. Please check your inbox for further details.", "warning")
                # send_confirmation_email(user)
            else:
                flash("Login Successfull!", "success")
            if form.email.data == "admin@admin.com" and current_user.role.role == "admin":
                return redirect(url_for("admin.index"))
            # If the user tries to access some route that requires login then
            # this line of code stores the url of that route and redirects the user
            # to that url after he has logged in successfully.
            next = request.args.get('next')
            return redirect(next or url_for('admin.index'))
        else:
            flash("Please check your email or password.", "danger")
        return redirect(url_for('auth.sign_in'))
    return render_template("auth/signin.html", title='Login', form=form)


@web_admin.route("/signOut", methods=['GET', 'POST'])
def sign_out():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect("/")