from market import app, db
from flask import render_template, redirect, url_for, flash
from market.models import User, Event, EventMembers,EventFields,UserEventFields
from market.forms import RegisterForm, LoginForm, EventForm, AddUserEvent,FieldsForm,UserFieldsForm
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
    user_events=EventMembers.query.filter_by(user_id=current_user.id,status='member').all()
    return render_template('dashboard.html',user_events=user_events)

@app.route("/events")
@login_required
def events_page():
    events=Event.query.order_by(Event.event_status.desc()).all()
    return render_template('events.html', events=events)


@app.route("/request_event/eventID=<int:event_id>/member=<int:member_id>", methods=['GET','POST'])
@login_required
def request_event(event_id,member_id):
        try:
            if EventMembers.query.filter_by(user_id=member_id, event_id=event_id, status='pending').first():
                flash('You already requested this event.', category='danger')
                return redirect(url_for('events_page'))
            if EventMembers.query.filter_by(user_id=member_id, event_id=event_id, status='member').first():
                flash('You\'re already a member of this event.', category='danger')
                return redirect(url_for('events_page'))
            if Event.query.filter_by(event_id=event_id, event_status='closed').first():
                flash('This event is closed! Sorry!', category='danger')
                return redirect(url_for('events_page'))
            
            user_to_add=EventMembers(user_id=member_id,event_id=event_id,status='pending')
            db.session.add(user_to_add)
            db.session.commit()
            flash('Request Successfull!', category='success')

        except:
            flash('Event Doesn\'t exist. Please Try A Different Event', category='danger')
            return redirect(url_for('events_page'))
        
        return redirect(url_for('events_page'))




@app.route("/delete_event/<int:event_id>", methods=['GET','POST'])
@login_required
def delete_event(event_id):
    event_to_delete=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id).delete()
            EventFields.query.filter_by(event_id=event_id).delete()
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






@app.route("/delete_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def delete_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id, user_id=member_id).delete()
            db.session.commit()
            flash('Successfully Deleted member!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error deleting member. Please try again.', category='danger')
    else:
        flash('You do not have permission to delete this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))



@app.route("/event-info/id=<int:event_id>", methods=['GET','POST'])
@login_required
def event_info(event_id):
    event = Event.query.filter_by(event_id=event_id).first()
    event_pending = EventMembers.query.filter_by(event_id=event_id,status='pending').first()
    event_fields = EventFields.query.filter_by(event_id=event_id).first()
    member_status = EventMembers.query.filter_by(event_id=event_id,user_id=current_user.id,status='member').first()

    
    



    if not event:
        flash('Event not found.', category='danger')
        return redirect(url_for('events_page'))
    
    form=AddUserEvent()
    fieldform=FieldsForm()
    userfieldsform=UserFieldsForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.username.data).one()
        except:
            flash('User not found.', category='danger')
            return redirect(url_for('event_info', event_id=event_id, event_pending=event_pending, event_fields=event_fields))
        
        if EventMembers.query.filter_by(user_id=user.id, event_id=event_id).first():
            flash('User is already a member of the event.', category='danger')
            return redirect(url_for('event_info', event_id=event_id, event_pending=event_pending, event_fields=event_fields))
        
        
        user_to_add=EventMembers(user_id=user.id,
                                 event_id=event_id,
                                 status='member')
        db.session.add(user_to_add)
        db.session.commit()
        flash('User Added Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error!: {err_msg}', category='danger')
                
                
    if fieldform.validate_on_submit():
        fields_to_add=EventFields(event_id=event_id,
                                  field_1=fieldform.field_1.data,
                                  field_2=fieldform.field_2.data,
                                  field_3=fieldform.field_3.data,
                                  field_4=fieldform.field_4.data,
                                  field_5=fieldform.field_5.data,
                                  field_6=fieldform.field_6.data,
                                  field_7=fieldform.field_7.data,
                                  field_8=fieldform.field_8.data,
                                  field_9=fieldform.field_9.data,
                                  field_10=fieldform.field_10.data)
        
        db.session.add(fields_to_add)
        db.session.commit()
        flash('Fields Added Successfully!', category='success')
        return redirect(url_for('event_info', event_id=event_id, event_pending=event_pending, event_fields=event_fields,userfieldsform=userfieldsform))
    
    if userfieldsform.validate_on_submit():
        pass
        
    
    return render_template("info.html",event=event, form=form, event_pending=event_pending, event_fields=event_fields, fieldform=fieldform,userfieldsform=userfieldsform,member_status=member_status)




@app.route("/create", methods=['GET','POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        current_date = datetime.utcnow().date()
        event_to_create=Event( coordinator_id=current_user.id,
                                event_name=form.event_name.data,
                                event_date=current_date,
                                event_status="open"
                              )
        db.session.add(event_to_create)
        db.session.commit()
        
        member_to_add = EventMembers(user_id=current_user.id,
                                     event_id=event_to_create.event_id,
                                     status='member')
        db.session.add(member_to_add)
        db.session.commit()


        flash('Event Created Successfully!', category='success')
        if form.errors !={}: #If there are not no errors from the validation
            for err_msg in form.errors.values():
                flash(f'There was an error with creating your event: {err_msg}', category='danger')
        return redirect(url_for('event_info', event_id=event_to_create.event_id))

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




@app.route("/accept_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def accept_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            member_to_update=EventMembers.query.filter_by(event_id=event_id, user_id=member_id).first()
            member_to_update.status='member'
            db.session.commit()
            flash('Successfully added member!', category='success')

        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error accepting member. Please try again.', category='danger')
    else:
        flash('You do not have permission to add this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))

@app.route("/decline_member/member=<int:member_id>/id=<int:event_id>", methods=['GET','POST'])
@login_required
def decline_member(member_id,event_id):
    event_to_delete_from=Event.query.get_or_404(event_id)
    if current_user.id == event_to_delete_from.coordinator_id:
        try:
            EventMembers.query.filter_by(event_id=event_id, user_id=member_id).delete()
            db.session.commit()
            flash('Successfully Declined Member!', category='success')
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('Error declining member. Please try again.', category='danger')
    else:
        flash('You do not have permission to Decline this member.', category='danger')
    return redirect(url_for('event_info', event_id=event_id))



@app.route("/start_event/id=<int:event_id>", methods=['GET','POST'])
@login_required
def start_event(event_id):
    event_to_update=Event.query.filter_by(event_id=event_id).first()
    event_to_update.event_status='closed'
    db.session.commit()
    
    
    return redirect(url_for('event_info', event_id=event_id))






