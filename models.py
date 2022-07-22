
import uuid
import sqlalchemy as sq
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError
from hashlib import md5


PG_DSN = "postgresql://oks:@localhost:5432/posts_flask"
engine = sq.create_engine(PG_DSN)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class UserModel(Base):
    __tablename__ = 'users'
    id = sq.Column(sq.Integer, primary_key=True)
    user_name = sq.Column(sq.String(100), unique=True, nullable=False)
    password = sq.Column(sq.String(100), nullable=False)
    email = sq.Column(sq.String, nullable=False, unique=True)
    registration = sq.Column(sq.DateTime, server_default=sq.func.now())
    advertisements = relationship('AdvertisementModel', backref='owner')
    token = relationship('Token', uselist=False, backref='user')
    
    def test_new_user():
        user = UserModel("qwa@mail.ru", "password")
        assert user.email == "qwa@mail.ru"
        assert user.token != "password"
        
    def to_dict(self):
        return {
            'user_name': self.user_name,
            'email': self.email,
            'registration': self.registration,
            'id': self.id,
            'password': self.password
        }

    @classmethod
    def register(cls, session: Session, user_name: str, password: str, email: str):
        new_user = UserModel(
            user_name=user_name,
            password=str(md5(password.encode()).hexdigest()),
            email=email
        )
        session.add(new_user)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
        else:
            token = Token(user_id=new_user.id)
            session.add(token)
            session.commit()
            return new_user

    @classmethod
    def get_all(cls, session):
        users = session.query(cls).all()
        return [user.to_dict() for user in users]


class AdvertisementModel(Base):
    __tablename__ = 'advertisement'
    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(500), nullable=False)
    description = sq.Column(sq.String, nullable=False)
    published_date = sq.Column(sq.DateTime, server_default=sq.func.now())
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))

    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'published_date': self.published_date,
            'id': self.id,
            'user_id': self.user_id
        }

    @classmethod
    def create(cls, session: Session, token, title: str, description: str):
        new_adv = AdvertisementModel(
            title=title,
            description=description,
            user_id=token.user_id
        )
        session.add(new_adv)
        session.commit()
        return new_adv

    @classmethod
    def get_all(cls, session):
        advertisements = session.query(cls).all()
        return [adv.to_dict() for adv in advertisements]


class Token(Base):
    __tablename__ = 'tokens'
    id = sq.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_date = sq.Column(sq.DateTime, server_default=sq.func.now())
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.id'))


Base.metadata.create_all(engine)
