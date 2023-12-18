from market import app, db
from flask import render_template, redirect, url_for, flash
from market.models import Item, User, Event, EventMembers
from market.forms import RegisterForm, LoginForm, EventForm, AddUserEvent
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
#flask_login helps with determining the current user, this is why we're able to use the variable current_user without declaring it in html

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404


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



@app.route("/events")
@login_required
def events_page():
    events=Event.query.all()
    return render_template('events.html', events=events)

@app.route("/delete_event/<int:event_id>", methods=['GET','POST'])
@login_required
def delete_event(event_id):
    event_to_delete=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id).delete()
            db.session.delete(event_to_delete)
            db.session.commit()
            flash('Successfully Deleted Event!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error deleting event. Please try again.', category='danger')
    else:
        flash('You do not have permission to delete this event.', category='danger')
    return redirect(url_for('events_page'))



@app.route("/event-info/id=<int:event_id>", methods=['GET','POST'])
@login_required
def event_info(event_id):
    event = Event.query.filter_by(event_id=event_id).first()
    if not event:
        flash('Event not found.', category='danger')
        return redirect(url_for('events_page'))
    form=AddUserEvent()
    
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except:
            flash('User not found.', category='danger')
            return redirect(url_for('event_info', event_id=event_id))
        
        if EventMembers.query.filter_by(user_id=user.id, event_id=event_id).first():
            flash('User is already a member of the event.', category='danger')
            return redirect(url_for('event_info', event_id=event_id))
        
        
        user_to_add=EventMembers(user_id=user.id,
                                 event_id=event_id)
        db.session.add(user_to_add)
        db.session.commit()
        flash('User Added Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error!: {err_msg}', category='danger')
    
    return render_template("info.html",event=event, form=form)




@app.route("/create", methods=['GET','POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        current_date = datetime.utcnow().date()
        event_to_create=Event( coordinator_id=current_user.id,
                                event_name=form.event_name.data,
                                event_date=current_date,
                              )
        db.session.add(event_to_create)
        db.session.commit()
        
        member_to_add = EventMembers(user_id=current_user.id,
                                     event_id=event_to_create.event_id)
        db.session.add(member_to_add)
        db.session.commit()

    
        flash('Event Created Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error with creating your event: {err_msg}', category='danger')

    return render_template('create.html', form=form)



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
        return redirect(url_for('dashboard_page'))
    
    #If one of the validations fails, the error will be stored in form.errors as a dictionary
    if form.errors !={}: #If there are not no errors from the validation
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
            return redirect(url_for('dashboard_page'))
        
        #This allows the user to login using their email as well
        elif (attempted_user_email and attempted_user_email.check_password_correction(attempted_password=form.password.data)):
            login_user(attempted_user_email)
            flash(f'Success! You are logged in as: {attempted_user_email.username}', category='success')
            return redirect(url_for('dashboard_page'))
        
        else:
            flash('Username and password are not a match! Please try again', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash('You have been logged out!', category='info')
    return redirect(url_for("home_page"))









