from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz


tz = pytz.timezone('Asia/Tashkent')


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    familiya = db.Column(db.String(), nullable=False)
    ism = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    dist = db.Column(db.Integer, nullable=False)
    roles = db.Column(db.String(), nullable=False)
    photo = db.Column(db.LargeBinary, nullable=True)

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    roles = db.Column(db.String(), nullable=False)
    role_name = db.Column(db.String(), nullable=False)

class UniversalTable(db.Model):
    __tablename__ = 'universal_table'

    id = db.Column(db.Integer, primary_key=True)
    district_fk = db.Column(db.Integer, nullable=False)
    section_fk = db.Column(db.Integer, nullable=False)
    vlan_fk = db.Column(db.Integer, nullable=False)
    vendor_fk = db.Column(db.Integer, nullable=False)
    hostname = db.Column(db.String(), nullable=False)
    ip_add = db.Column(db.String(), nullable=False)
    mask = db.Column(db.String(), nullable=False)
    mac_add = db.Column(db.String(), unique=True, nullable=False)

class District(db.Model):
    __tablename__ = 'district'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    short = db.Column(db.String(255))

class Vlan(db.Model):
    __tablename__ = 'vlan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vlan_id = db.Column(db.String(255), nullable=False)

class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    okrug_fk = db.Column(db.Integer, nullable=False)

class Vendor(db.Model):
    __tablename__ = 'vendor'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

class DeviceBackup(db.Model):
    __tablename__ = 'backup_device'
    id = db.Column(db.Integer, primary_key=True)
    file_ip = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    files = db.Column(db.LargeBinary)
    data_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now(tz))

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime, default=None)
    active = db.Column(db.Boolean, default=True)


class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    district = db.Column(db.String, nullable=False)
    roles = db.Column(db.String, nullable=False)
    actions = db.Column(db.String, nullable=False)
    times = db.Column(db.DateTime, nullable=False)
    dates = db.Column(db.Date, nullable=False)


class Backup_list(db.Model):
    __tablename__ = 'backup_list'
    id = db.Column(db.Integer, primary_key=True)
    okrug = db.Column(db.Integer, nullable=False)
    qism = db.Column(db.Integer, nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    ip_add = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(255))
    vendor = db.Column(db.Integer, nullable=False)


