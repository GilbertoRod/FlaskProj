from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin

#UserMixin allows is_authenticated


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    first_name = db.Column(db.String(length=50), nullable=False)
    last_name = db.Column(db.String(length=50), nullable=False)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    items = db.relationship('Item', backref='owned_user', lazy=True)
    events = db.relationship('Event', backref='coordinator', lazy=True)
    events_attending = db.relationship('EventMembers', backref='attendees', lazy=True)

    


    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'))
    def __repr__(self):
        return f'Item {self.name}'
    

class Event(db.Model):
    event_id = db.Column(db.Integer(), primary_key=True)
    coordinator_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    event_name = db.Column(db.String(length=75), nullable=False, unique=True)
    event_date = db.Column(db.Date())
    event_status = db.Column(db.String(length=20))
    members = db.relationship('EventMembers', backref='attended_events', lazy=True)
    fields = db.relationship('EventFields', backref='event_for_field', lazy=True)
    

    def __repr__(self):
        return f'Event {self.event_name}'
    

class EventMembers(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    event_id = db.Column(db.Integer(), db.ForeignKey('event.event_id'), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(length=20))
    user = db.relationship('User', backref='event_members', lazy=True)

class EventFields(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    event_id = db.Column(db.Integer(), db.ForeignKey('event.event_id'), nullable=False)
    field_1 = db.Column(db.String(length=150), nullable=False)
    field_2 = db.Column(db.String(length=150))
    field_3 = db.Column(db.String(length=150))
    field_4 = db.Column(db.String(length=150))
    field_5 = db.Column(db.String(length=150))
    field_6 = db.Column(db.String(length=150))
    field_7 = db.Column(db.String(length=150))
    field_8 = db.Column(db.String(length=150))
    field_9 = db.Column(db.String(length=150))
    field_10 = db.Column(db.String(length=150))
    

class UserEventFields(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    field_id = db.Column(db.Integer(), db.ForeignKey('event_fields.id'), nullable=False)
    event_id = db.Column(db.Integer(), db.ForeignKey('event.event_id'), nullable=False, unique=True)
    field_1 = db.Column(db.String(length=150))
    field_2 = db.Column(db.String(length=150))
    field_3 = db.Column(db.String(length=150))
    field_4 = db.Column(db.String(length=150))
    field_5 = db.Column(db.String(length=150))
    field_6 = db.Column(db.String(length=150))
    field_7 = db.Column(db.String(length=150))
    field_8 = db.Column(db.String(length=150))
    field_9 = db.Column(db.String(length=150))
    field_10 = db.Column(db.String(length=150))