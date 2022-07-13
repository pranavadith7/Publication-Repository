from repository import db, login, app
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import url_for
import enum, uuid

class PaperAccessEnum(enum.Enum):
    ALLOW_ALL = 'Allow All'
    ONLY_YOUR_COLLEGE = 'Only Faculties and Your College Students'
    ONLY_FACULTIES = 'Faculties Only'

    @staticmethod
    def fetch_fields():
        return [(c.name, c.value) for c in PaperAccessEnum]


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<Role '{}'>".format(self.name)


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True, nullable=False)
    student_email_server = db.Column(db.String(128), unique=True, index=True, nullable=False)
    users = db.relationship('User', backref='institution', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<Institution: '{}', StudentEmailServer: '{}'>".format(self.name, self.student_email_server)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(64), index=True)
    lname = db.Column(db.String(64), index=True)
    profile_image = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(120), index=True, unique=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institution.id'), nullable=False)
    password_hash = db.Column(db.String(128))
    by_email = db.Column(db.Boolean, default=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    faculty = db.relationship("Faculty", back_populates="user", uselist=False)

    @staticmethod
    def getWhoCanPublish():
        return User.query.join(Role).filter(Role.name!="student").all()

    @staticmethod
    def getFaculties():
        return User.query.join(Role).filter(Role.name=="faculty").all()

    @staticmethod
    def getStudents():
        return User.query.join(Role).filter(Role.name=="student").all()

    @staticmethod
    def getPanels():
        return User.query.join(Role).filter(Role.name=="panel").all()

    def get_reset_token(self, expires_sec=1200):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def get_profile_image_url(self, img_size=64):
        if self.profile_image:
            return url_for('static', filename='profile_pics/' + self.profile_image)
        else:
            bg_and_color_list = [('0D8ABC', 'fff'), ('a0a0a0', 'ff0'), ('ff0000', 'fff'), ('40e0d0', '000')]
            bg_lis_len = len(bg_and_color_list)
            user_bg = bg_and_color_list[self.id % bg_lis_len]
            return f'https://ui-avatars.com/api/?name={self.fname}+{self.lname}' + f'&background={user_bg[0]}&color={user_bg[1]}&size={img_size}'


    def publications(self):
        return PublishPaper.query.filter(PublishPaper.authors.any(User.id == self.id)).all()

    def publications_object(self):
        return PublishPaper.query.filter(PublishPaper.authors.any(User.id == self.id))

    def pending_publications(self):
        return PublishPaper.query.filter(PublishPaper.authors.any(User.id == self.id), PublishPaper.is_paper_authorized==None).all()

    def authorized_publications(self):
        return PublishPaper.query.filter(PublishPaper.authors.any(User.id == self.id), PublishPaper.is_paper_authorized==True).all()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User id: '{}', Name: '{}'>".format(self.id, self.fname + " " + self.lname)


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    department_areas = db.relationship('DepartmentAreas', backref='department', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<Community '{}'>".format(self.name)

class DepartmentAreas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    publish_papers = db.relationship('PublishPaper', backref='department_area', lazy=True) # new for publish_paper
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<Department Area: '{}'>".format(self.name)

class PaperType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    publish_papers = db.relationship('PublishPaper', backref='paper_type', lazy=True) # new for publish_paper
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return "<PaperType: '{}'>".format(self.name)

author_publish_paper = db.Table('author_publish_papers',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('publish_paper_id', db.Integer, db.ForeignKey('publish_paper.id'), primary_key=True)
)

citations_tree = db.Table(
    'citations_tree',
    db.Column('citedby_id', db.Integer, db.ForeignKey('publish_paper.id')),
    db.Column('citation_id', db.Integer, db.ForeignKey('publish_paper.id'))
)

class PublishPaper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    abstract = db.Column(db.Text())
    unique_paper_id = db.Column(db.String(16), unique=True)
    paper_type_id = db.Column(db.Integer, db.ForeignKey('paper_type.id'), nullable=False) # new for publish_paper
    department_area_id = db.Column(db.Integer, db.ForeignKey('department_areas.id'), nullable=False) # new for publish_paper # Appears in Collection
    authors = db.relationship('User', secondary=author_publish_paper, lazy='subquery',
        backref=db.backref('publish_papers', lazy=True))
    publisher = db.Column(db.String(255), nullable=False)
    published_year = db.Column(db.Integer, nullable=False, default=datetime.utcnow().year)
    paper_file = db.Column(db.String(155), nullable=True)
    access = db.Column(db.Enum(PaperAccessEnum), default=PaperAccessEnum.ALLOW_ALL)
    is_paper_authorized = db.Column(db.Boolean, nullable=True)
    citations = db.relationship(
        'PublishPaper',
        secondary=citations_tree,
        primaryjoin=(citations_tree.c.citedby_id == id),
        secondaryjoin=(citations_tree.c.citation_id == id),
        backref=db.backref('citedby', lazy='dynamic'),
        lazy='dynamic'
    )

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @staticmethod
    def get_pending_papers():
        return PublishPaper.query.filter_by(is_paper_authorized=None).all()

    @staticmethod
    def generate_unique_paper_id():
        uu = uuid.uuid4().hex[:8]
        while PublishPaper.query.filter_by(unique_paper_id=uu).first() != None:
            uu = uuid.uuid4().hex[:8]
        return uu


    def authorize_paper(self):
        self.is_paper_authorized = True

    def reject_paper(self):
        self.is_paper_authorized = False

    def set_pending(self):
        self.is_paper_authorized = None

    def get_paper_file_url(self):
        if self.paper_file:
            return url_for('pub_file', paper_id=self.id, filename=self.paper_file)

    def get_paper_name(self):
        if self.paper_file:
            return "_".join(self.paper_file.split("-")[1:])

    def get_paper_size(self, unit=None):
        file_size = os.stat(os.path.join(app.root_path, 'protected', self.paper_file)).st_size
        if unit == "KB":
            file_size = str(round(file_size / 1024, 3))
        elif unit == "MB":
            file_size = str(round(file_size / (1024 * 1024), 3))
        return file_size

    def __repr__(self):
        return "<PublishPaper: '{}'>".format(self.title[:50] + (self.title[50:] and '..'))

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    about_me = db.Column(db.Text, nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    linkedin = db.Column(db.String(150), nullable=True)
    github = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable = True)
    address = db.Column(db.String(100), nullable = True)
    work_exp = db.Column(db.String(255), nullable = True)
    currently_working = db.Column(db.Text, nullable=True)
    conference_attended = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="faculty")

    def publications(self):
        return PublishPaper.query.filter(PublishPaper.authors.any(User.id == self.user_id)).all()
