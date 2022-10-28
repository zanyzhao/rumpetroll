import json

from pbkdf2 import crypt
from settings import Base
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Float,
)


class Users(Base):
    """用户注册信息"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), nullable=False, unique=True)  # 不允许为空且唯一
    _password = Column("password", String(100))
    createtime = Column(DateTime, default=datetime.now)
    winnums = Column(Integer, default=0)  # 赢的总次数
    gender = Column(String(3), nullable=False)
    # openid = Column(String(50), nullable=False)
    # openpwd = Column(String(50), nullable=False)

    def _hash_password(self, password):
        return crypt(password, iterations=0x2537)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = self._hash_password(password)

    def auth_password(self, pwd):
        if self._password:
            return self.password == crypt(pwd, self.password)
        else:
            return False

    # @property
    # def serialize(self):
    #     return self.to_json(self, self.__class__)
    #
    # def to_json(self, inst, cls):
    #     d = dict()
    #     for c in cls.__table__.columns:
    #         v = getattr(inst, c.name)
    #         d[c.name] = v
    #     return json.dumps(d)

    # def to_json(self, inst, cls):
    #     dict = self.__dict__
    #     if "_sa_instalce_state" in dict:
    #         del dict["_sa_instalce_state"]
    #     return dict

class UserGolds(Base):
    """蝌蚪每局吃的金币数排名"""
    __tablename__ = "user_golds"
    id = Column(Integer, primary_key=True, autoincrement=True)
    rooms = Column(Integer, nullable=False)  # 房间号
    golds = Column(Integer)  # 吃的金币数
    sank = Column(Integer, default=0)  # 排名，默认不排名
    createtime = Column(DateTime, default=datetime.now)
    server = Column(String(30))  # 所在的服务器
