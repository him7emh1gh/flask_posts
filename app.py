import flask
from flask import request
from flask.views import MethodView
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


app = flask.Flask('app')
PG_DSN = "postgresql://admin:1234@127.0.0.1:5432/flask_netology"
engine = sq.create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class UserModel(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    user_name = sq.Column(sq.String(100), unique=True, nullable=False)
    password = sq.Column(sq.String(100), nullable=False)
    registration = sq.Column(sq.DateTime, server_default=sq.func.now())
    advertisements = relationship('Advertisement', backref='user')


class AdvertisementModel(Base):
    __tablename__ = 'advertisement'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(500), nullable=False)
    description = sq.Column(sq.String, nullable=False)
    published_date = sq.Column(sq.DateTime, server_default=sq.func.now())
    user_id = sq.Column(sq.Integer, sq.ForeignKey('user.id'))


class UserView(MethodView):
    def get(self):
        pass

    def post(self):
        new_user_data = request.json
        with Session() as session:
            new_user = UserModel(
                user_name=new_user_data['user_name'],
                password=new_user_data['password']
            )
            session.add(new_user)
            session.commit()
            return flask.jsonify({
                'id': new_user.id
            })

app.add_url_rule('/user', view_func=UserView.as_view('create_user'), methods=['POST',])

Base.metadata.create_all(engine)