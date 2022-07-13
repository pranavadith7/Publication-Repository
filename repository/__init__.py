import asyncio
import os
from flask import Flask, flash, redirect, url_for, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose
from flask_executor import Executor
from flask_admin.contrib import sqla as flask_admin_sqla
from authlib.integrations.flask_client import OAuth
# from flask_mailing import Mail

import smtplib
from email.message import Message
# from flask_mailing import Message
from sqlalchemy import func, text

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'
login.login_message = 'You need to be logged in to view this page'
login.login_message_category = 'info'
executor = Executor(app)

# Mail
# mail = Mail(app)

# GitHub Configuration
oauth = OAuth(app)
github = oauth.register(
    name='github',
    client_id=os.environ.get("CLIENT_ID"),
    client_secret=os.environ.get("SECRET_ID"),
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)

from repository import routes, models
from flask_admin.menu import MenuLink

class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated

# Admin
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        is_acc = current_user.is_authenticated and current_user.role.name == "admin"
        if not is_acc:
            flash("You need to login", "success")
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    @expose('/')
    def index(self):
        departments = models.Department.query.all()
        page = request.args.get('author_page', 1, type=int)
        authors = db.session.query(models.User, func.count(models.author_publish_paper.c.user_id).label('total')) \
            .join(models.author_publish_paper).join(models.Role).filter(models.Role.name!="student") \
            .group_by(models.User).order_by(text('total DESC')).paginate(page, 8, False)
        return self.render('admin_index.html', arg1="hi", departments=departments, authors=authors)


class DefaultModelView(flask_admin_sqla.ModelView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        is_acc = current_user.is_authenticated and current_user.role.name == "admin"
        if not is_acc:
            flash("You need to login And you chould be admin", "success")
        return is_acc

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))


admin = Admin(app, name='Faculty Publication Repo Admin', template_mode='bootstrap3', index_view=MyAdminIndexView())
# admin = Admin(app, name='Faculty Publication Repo Admin', template_mode='bootstrap3')
admin.add_view(DefaultModelView(models.Role, db.session))
admin.add_view(DefaultModelView(models.Institution, db.session))
admin.add_view(DefaultModelView(models.User, db.session))
admin.add_view(DefaultModelView(models.Faculty, db.session))
admin.add_view(DefaultModelView(models.Department, db.session))
admin.add_view(DefaultModelView(models.DepartmentAreas, db.session))
admin.add_view(DefaultModelView(models.PaperType, db.session))
admin.add_view(DefaultModelView(models.PublishPaper, db.session))
admin.add_link(LogoutMenuLink(name='Logout', category='', url='/logout'))
admin.add_link(LoginMenuLink(name='Login', category='', url='/users/login'))

class AnalyticsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('analytics_index.html')

class PendingPaper(BaseView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def is_accessible(self):
        is_acc = current_user.is_authenticated and current_user.role.name == "admin"
        if not is_acc:
            flash("You need to login And you should be admin", "success")
        return is_acc

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

    def send_rejection_mail(self, paper, recipients, reason):
        msg = Message()
        msg['Subject'] = "Paper Request Rejection"
        msg['From'] = app.config['NOREPLY_NAME']
        msg['To'] = ", ".join(recipients)
        msg.add_header('Content-Type','text/html')
        message = """Sorry, Your request to the paper of title <h2 style='display: inline-block;'>{}</h2> is <b>rejected</b>, And here is the reason why?\n<b>{}</b>""".format(paper.title, reason)
        msg.set_payload(message)

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(msg['From'], recipients, msg.as_string())

    def send_approved_mail(self, paper, recipients):
        msg = Message()
        msg['Subject'] = "Paper Request Approval"
        msg['From'] = app.config['NOREPLY_NAME']
        msg['To'] = ", ".join(recipients)
        msg.add_header('Content-Type','text/html')
        message = """Congratulations! Your request to the paper of title <h2 style='display: inline-block;'>{}</h2> is <b>Approved</b>""".format(paper.title)
        msg.set_payload(message)

        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.sendmail(msg['From'], recipients, msg.as_string())

    @expose('/')
    def index(self):
        papers = models.PublishPaper.query.filter_by(is_paper_authorized=None).all()
        return self.render('pending_paper_index.html', papers=papers)

    @expose('/approve/<int:id>', methods=['GET', 'POST'])
    def approve_paper(self, id):
        paper = models.PublishPaper.query.get_or_404(id)
        emails = [u.email for u in paper.authors]

        if request.method == 'POST':
            reject_reason = request.form.get('reject_reason')
            if reject_reason == "" :
                flash("Enter a valid reason", "warning")
                return redirect(url_for('pending_paper.index'))

            paper.is_paper_authorized = False
            db.session.commit()
            executor.submit(self.send_rejection_mail, paper, emails, reject_reason)
            # loop = None
            # try:
            #     loop = asyncio.get_event_loop()
            # except RuntimeError as ex:
            #     if "There is no current event loop in thread" in str(ex):
            #         loop = asyncio.new_event_loop()
            #         asyncio.set_event_loop(loop)
            #         loop = asyncio.get_event_loop()
            # loop.run_until_complete(self.send_rejection_mail(paper, emails, reject_reason))
            # loop.close()
            return redirect(url_for('pending_paper.index'))

        paper.is_paper_authorized = True
        db.session.commit()
        executor.submit(self.send_approved_mail, paper, emails)
        # loop = None
        # try:
        #     loop = asyncio.get_event_loop()
        # except RuntimeError as ex:
        #     if "There is no current event loop in thread" in str(ex):
        #         loop = asyncio.new_event_loop()
        #         asyncio.set_event_loop(loop)
        #         loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.send_approved_mail(paper, emails))
        # loop.close()
        return redirect(url_for('pending_paper.index'))

admin.add_view(AnalyticsView(name='Analytics', endpoint='analytics'))
admin.add_view(PendingPaper(name='PendingPaper', endpoint='pending_paper'))
