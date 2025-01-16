import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Semestre(db.Model):
    __tablename__ = 'semestres'
    id = db.Column(db.Integer, primary_key=True)
    name_semestre = db.Column(db.String(64), unique=True)
    disciplinas = db.relationship('Disciplina', backref='semestre', lazy='dynamic')

    def __repr__(self):
        return '<Semestre %r>' % self.name_semestre


class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    name_disciplina = db.Column(db.String(64), unique=True, index=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestres.id'))

    def __repr__(self):
        return '<Disciplina %r>' % self.name_disciplina

class NameForm(FlaskForm):
    disciplina = StringField('Cadastre a nova disciplina e o semestre associado:', validators=[DataRequired()])
    semestre = RadioField(choices=[('1º semestre'),
                                ('2º semestre'),
                                ('3º semestre'),
                                ('4º semestre'),
                                ('5º semestre'),
                                ('6º semestre')])
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Disciplina=Disciplina, Semestre=Semestre)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', current_time=datetime.utcnow()), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=datetime.utcnow()), 500

@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())

@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = NameForm()
    disciplinas = Disciplina.query.all()
    semestres = Semestre.query.all()
    if form.validate_on_submit():
        disciplina = Disciplina.query.filter_by(name_disciplina=form.disciplina.data).first()
        if not disciplina:
            semestre = Semestre.query.filter_by(name_semestre=form.semestre.data).first()
            disciplina = Disciplina(name_disciplina=form.disciplina.data, semestre=semestre)
            db.session.add(disciplina)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
            flash('Disciplina já existe na base de dados!')
        session['disciplina'] = form.disciplina.data
        session['semestre'] = form.semestre.data
        return redirect(url_for('disciplinas'))
    return render_template('disciplinas.html',
                           form=form,
                           name=session.get('disciplina'),
                           known=session.get('known', False),
                           disciplinas=disciplinas,
                           semestres=semestres)