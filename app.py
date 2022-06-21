import pydantic
import flask
from flask import request, jsonify
from flask.views import MethodView
from hashlib import md5
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

from models import UserModel, AdvertisementModel, Session, Token


app = flask.Flask('app')


class HTTPError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message


@app.errorhandler(HTTPError)
def handle_invalid_usage(error):
    response = jsonify({"message": error.message})
    response.status_code = error.status_code
    return response


class CreateUserModel(pydantic.BaseModel):
    user_name: str
    password: str
    email: str


class CreateAdvertisementModel(pydantic.BaseModel):
    title: str
    description: str


def validate(data: dict, validation_model):
    try:
        return validation_model(**data).dict()
    except pydantic.ValidationError as er:
        raise HTTPError(400, er.errors())


def check_token(session: Session):
    request_token = request.headers.get('token')
    token = session.query(Token).filter(Token.id == request_token).first()
    if token is None:
        raise HTTPError(401, 'Invalid Token')
    return token


def is_owner(session, adv_id, token):
    adv_owner = session.query(AdvertisementModel).filter_by(id=adv_id).first()
    if not adv_owner:
        raise HTTPError(404, 'invalid advertisement id')
    if token.user_id != adv_owner.user_id:
        raise HTTPError(403, 'auth error')
    return True


class UserView(MethodView):

    def get(self, user_id: int=None):
        with Session() as session:
            if user_id:
                user = session.query(UserModel).filter_by(id=user_id).first()
                return jsonify(user.to_dict())
            else:
                return jsonify(UserModel.get_all(session))

    def post(self):
        with Session() as session:
            new_user_data = validate(request.json, CreateUserModel)
            new_user = UserModel.register(session, **new_user_data)
            return jsonify(new_user.to_dict())


class AdvertisementView(MethodView):

    def get(self, adv_id: int=None):
        with Session() as session:
            if adv_id:
                adv = session.query(AdvertisementModel).filter_by(id=adv_id).first()
                return jsonify(adv.to_dict())
            else:
                return jsonify(AdvertisementModel.get_all(session))


    def post(self):
        new_adv_data = validate(request.json, CreateAdvertisementModel)
        with Session() as session:
            token = check_token(session)
            new_adv = AdvertisementModel.create(session, token, **new_adv_data)
            return jsonify(new_adv.to_dict())

    def patch(self, adv_id: int):
        with Session() as session:
            token = check_token(session)
            if is_owner(session, adv_id, token):
                session.query(AdvertisementModel).filter_by(id=adv_id).update(request.json)
                session.commit()
            raise HTTPError(201, 'successfully updated')

    def delete(self, adv_id: int):
        with Session() as session:
            token = check_token(session)
            if is_owner(session, adv_id, token):
                adv_for_del = session.query(AdvertisementModel).filter_by(id=adv_id).first()
                session.delete(adv_for_del)
                session.commit()
            raise HTTPError(204, 'successfully deleted')

app.add_url_rule(
    '/user',
    view_func=UserView.as_view('create_user'),
    methods=['POST', 'GET', ]
)
app.add_url_rule(
    '/user/<int:user_id>',
    view_func=UserView.as_view('get_user'),
    methods=['GET', ]
)
app.add_url_rule(
    '/advertisement',
    view_func=AdvertisementView.as_view('create_or_get_all_adv'),
    methods=['POST', 'GET', ]
)
app.add_url_rule(
    '/advertisement/<int:adv_id>',
    view_func=AdvertisementView.as_view('work_with_adv'),
    methods=['PATCH', 'GET', 'DELETE']
)

print('DB is ready')
app.run()
