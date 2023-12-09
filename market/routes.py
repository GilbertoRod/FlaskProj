from market import app, db
from flask import render_template, redirect, url_for, flash
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, ProfileForm
from flask_login import login_user, logout_user, login_required, current_user
#flask_login helps with determining the current user, this is why we're able to use the variable current_user without declaring it in html

@app.route("/")
@app.route("/home")
def home_page():
    return render_template('home.html')


@app.route("/dashboard")
@login_required
def dashboard_page():
    return render_template('dashboard.html')




@app.route("/entries")
@login_required
def entries_page():
    items=Item.query.all()
    return render_template('entries.html', items=items)

@app.route("/register", methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create=User(username=form.username.data,
                            first_name=form.first_name.data,
                            last_name=form.last_name.data,
                            email_address=form.email_address.data,
                            password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()

        login_user(user_to_create)
        flash(f'Account Created Successfully! You are now logged in as {user_to_create.username}', category='success')
        return redirect(url_for('entries_page'))
    
    #If one of the validations fails, the error will be stored in form.errors as a dictionary
    if form.errors !={}: #If there are no errors from the validation
        for err_msg in form.errors.values():
            flash(f'There was an error with creating your account: {err_msg}', category='danger')

    return render_template('register.html',form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        attempted_user_email = User.query.filter_by(email_address=form.username.data).first()

        if (attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data)) :
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('entries_page'))
        
        #This allows the user to login using their email as well
        elif (attempted_user_email and attempted_user_email.check_password_correction(attempted_password=form.password.data)):
            login_user(attempted_user_email)
            flash(f'Success! You are logged in as: {attempted_user_email.username}', category='success')
            return redirect(url_for('entries_page'))
        
        else:
            flash('Username and password are not a match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for("home_page"))
