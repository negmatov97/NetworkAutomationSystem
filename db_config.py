from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import BIGINT
from datetime import datetime
import pytz
from werkzeug.security import generate_password_hash

tz = pytz.timezone('Asia/Tashkent')


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'admins'

    id = db.Column(BIGINT, primary_key=True, autoincrement=True)
    familiya = db.Column(db.String(), nullable=False)
    ism = db.Column(db.String(), nullable=False)
    username = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    dist = db.Column(db.Integer, db.ForeignKey('district.id', ondelete='CASCADE'), nullable=False)
    roles = db.Column(db.String, db.ForeignKey('roles.roles', ondelete='CASCADE'), nullable=False)

    district = db.relationship('District', backref=db.backref('admins', cascade='all, delete', lazy='dynamic'))
    role = db.relationship('Roles', backref=db.backref('admins', cascade='all, delete', lazy='dynamic'))

class Roles(db.Model):
    __tablename__ = 'roles'

    id = db.Column(BIGINT, primary_key=True, autoincrement=True)
    roles = db.Column(db.String, unique=True, nullable=False)
    role_name = db.Column(db.String(), nullable=False)

class UniversalTable(db.Model):
    __tablename__ = 'universal_table'

    id = db.Column(db.Integer, primary_key=True)
    district_fk = db.Column(db.Integer, db.ForeignKey('district.id', ondelete='CASCADE'), nullable=False)
    section_fk = db.Column(db.Integer, db.ForeignKey('section.id', ondelete='CASCADE'), nullable=False)
    vlan_fk = db.Column(db.Integer, db.ForeignKey('vlan.id', ondelete='CASCADE'), nullable=False)
    vendor_fk = db.Column(db.Integer, db.ForeignKey('vendor.id', ondelete='CASCADE'), nullable=False)
    hostname = db.Column(db.String(), nullable=False)
    ip_add = db.Column(db.String(), nullable=False)
    mask = db.Column(db.String(), nullable=False)
    mac_add = db.Column(db.String(), unique=True, nullable=False)

    district = db.relationship('District', backref=db.backref('universal_table', cascade='all, delete', lazy='dynamic'))
    section = db.relationship('Section', backref=db.backref('universal_table', cascade='all, delete', lazy='dynamic'))
    vlan = db.relationship('Vlan', backref=db.backref('universal_table', cascade='all, delete', lazy='dynamic'))
    vendor = db.relationship('Vendor', backref=db.backref('universal_table', cascade='all, delete', lazy='dynamic'))

class District(db.Model):
    __tablename__ = 'district'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    short = db.Column(db.String(255), nullable=False)

class Section(db.Model):
    __tablename__ = 'section'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    okrug_fk = db.Column(db.Integer, db.ForeignKey('district.id', ondelete='CASCADE'), nullable=False)

    district = db.relationship('District', backref=db.backref('sections', cascade='all, delete', lazy='dynamic'))

class Backup_list(db.Model):
    __tablename__ = 'backup_list'
    id = db.Column(db.Integer, primary_key=True)
    okrug = db.Column(db.Integer, db.ForeignKey('district.id', ondelete='CASCADE'), nullable=False)
    qism = db.Column(db.Integer, db.ForeignKey('section.id', ondelete='CASCADE'), nullable=False)
    hostname = db.Column(db.String(255), nullable=False)
    ip_add = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.String(255))
    vendor = db.Column(db.Integer, db.ForeignKey('vendor.id', ondelete='CASCADE'), nullable=False)

    district = db.relationship('District', backref=db.backref('backup_lists', cascade='all, delete', lazy='dynamic'))
    section = db.relationship('Section', backref=db.backref('backup_lists', cascade='all, delete', lazy='dynamic'))
    vendors = db.relationship('Vendor', backref=db.backref('backup_lists', cascade='all, delete', lazy='dynamic'))


class Vlan(db.Model):
    __tablename__ = 'vlan'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    vlan_id = db.Column(db.String(255), nullable=False)

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

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    district = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.String(255), nullable=False)
    actions = db.Column(db.String(255), nullable=False)
    times = db.Column(db.DateTime, nullable=False, default=datetime.now)
    dates = db.Column(db.Date, nullable=False, default=datetime.today)


def seed_data():
    # Boshlang'ich tuman va rollarni qo'shing
    district = [
        District(name="Tashkent", short="TSH"),
        District(name="Andijon", short="ANJ"),
        District(name="Buxoro", short="BX"),
        District(name="Farg'ona", short="FRG"),
        District(name="Jizzax", short="JZ"),
        District(name="Namangan", short="NM"),
        District(name="Navoiy", short="NV"),
        District(name="Qashqadaryo", short="QSH"),
        District(name="Samarqand", short="SMR"),
        District(name="Sirdaryo", short="SRD"),
        District(name="Surxondaryo", short="SRX"),
        District(name="Xorazm", short="XZ"),
        District(name="Qoraqalpog'iston", short="QRP")
    ]

    role = [
        Roles(roles="S_admin", role_name="Super Admin"),
        Roles(roles="D_admin", role_name="District Admin"),
        Roles(roles="RO_admin", role_name="Read Only Admin")
    ]

    section = [
        Section(name="Mirzo Ulug'bek", okrug_fk=1),
        Section(name="Asaka", okrug_fk=2),
        Section(name="Buxoro", okrug_fk=3),
        Section(name="Bog'dod", okrug_fk=4),
        Section(name="Jizzax", okrug_fk=5),
        Section(name="Namangan", okrug_fk=6),
        Section(name="Navoiy", okrug_fk=7),
        Section(name="Qarshi", okrug_fk=8),
        Section(name="Samarqand", okrug_fk=9),
        Section(name="Guliston", okrug_fk=10),
        Section(name="Termiz", okrug_fk=11),
        Section(name="Urganch", okrug_fk=12),
        Section(name="Nukus", okrug_fk=13)
    ]

    vlan = [
        Vlan(name="MGMT_1", vlan_id="2443"),
        Vlan(name="MGMT_2", vlan_id="2443")
    ]

    vendor = [
        Vendor(name="SNR-S2982G-24T-POE"),
        Vendor(name="SNR-S2985G-24TC"),
        Vendor(name="S4600-28P-P-SI"),
        Vendor(name="TL-SG3210")
    ]

    try:

        db.session.add_all(district)
        db.session.add_all(role)
        db.session.add_all(vlan)
        db.session.add_all(section)
        db.session.add_all(vendor)

        # Admin foydalanuvchi qo'shing
        admin_user = User(
            familiya="Adminov",
            ism="Admin",
            username="admin",
            password=generate_password_hash("admin123"),  # Parolni hashlash
            dist=1,
            roles="S_admin"
        )

        db.session.add(admin_user)
        db.session.commit()

        print("Boshlang'ich ma'lumotlar muvaffaqiyatli qo'shildi!")

    except Exception as e:
        db.session.rollback()
        print(f"Xato yuz berdi: {e}")




