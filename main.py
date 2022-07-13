import os
from repository import app, db
from repository.models import User, Role, Institution, Department, DepartmentAreas, PaperType, \
    PublishPaper, author_publish_paper, PaperAccessEnum

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Role': Role, 'Institution': Institution,
        'Department': Department, 'DepartmentAreas': DepartmentAreas, 'PaperType': PaperType, 'PublishPaper': PublishPaper,
            'author_publish_paper': author_publish_paper, 'PaperAccessEnum': PaperAccessEnum}

if __name__ == '__main__':
    # app.run()
    app.run(ssl_context='adhoc')
