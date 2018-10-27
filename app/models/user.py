from sqlalchemy import Column, Integer, String, SmallInteger
from werkzeug.security import generate_password_hash, check_password_hash

from app.libs.enums import ScopeEnum
from app.libs.error_code import AuthFailed, NotFound
from app.models.base import Base, db
from app.service.user_token import UserToken


class User(Base):
    id = Column(Integer, primary_key=True)
    openid = Column(String(50), unique=True)
    email = Column(String(24), unique=True)
    nickname = Column(String(24))
    userPic = Column(String(255))
    auth = Column(SmallInteger, default=1)
    _password = Column('password', String(100))

    def keys(self):
        self.hide('openid', '_password').append('create_datetime')
        return self.fields

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, raw):
        self._password = generate_password_hash(raw)

    @staticmethod
    def register_by_email(nickname, account, secret):
        with db.auto_commit():
            user = User()
            user.nickname = nickname
            user.email = account
            user.password = secret
            db.session.add(user)

    @staticmethod
    def register_by_wx(account):
        with db.auto_commit():
            user = User()
            user.openid = account
            db.session.add(user)
        return User.query.filter_by(openid=account).first()

    @staticmethod
    def verify_by_email(email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise NotFound()
        if not user.check_password(password):
            raise AuthFailed()
        scope = 'AdminScope' if user.auth == ScopeEnum.Admin else 'UserScope'
        return {'uid': user.id, 'scope': scope}

    @staticmethod
    def verify_by_wx(code, *args):
        ut = UserToken(code)
        wx_result = ut.get()
        openid = wx_result['openid']
        user = User.query.filter_by(openid=openid).first()
        if not user:
            user = User.register_by_wx(openid)
        scope = 'AdminScope' if user.auth == ScopeEnum.Admin else 'UserScope'
        return {'uid': user.id, 'scope': scope}

    def check_password(self, raw):
        if not self._password:
            return False
        return check_password_hash(self._password, raw)
