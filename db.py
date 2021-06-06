from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Integer, String, ForeignKey, DateTime, Column, INTEGER, Float, func, Index, event
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, LONGTEXT, SMALLINT, TINYINT
from sqlalchemy_utils import ChoiceType
from confs.config import MYSQL_CONFIG


engine = create_engine('mysql+pymysql://{user}:{password}@{host}:{port}/{db}'.format(**MYSQL_CONFIG),
                       pool_recycle=3600, encoding='utf-8')

Base = declarative_base()


class Role(Base):
    """
    角色
    """
    __tablename__ = 'role'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(128), nullable=False, comment='角色名')
    code = Column(Integer, unique=True, nullable=False, comment='角色编号')
    update_time = Column(DATETIME, server_default=func.now(), onupdate=func.now(), nullable=False, comment='更新时间')
    create_time = Column(DATETIME, server_default=func.now(), nullable=False, comment='创建时间')

    __table_args__ = ({'comment': '角色'})


class User(Base):
    """
    用户信息
    """
    __tablename__ = 'user'

    id = Column(INTEGER(11), primary_key=True)
    account = Column(String(128), nullable=False, unique=True, comment='登录账号')
    username = Column(String(128), nullable=False, comment='用户姓名')
    password = Column(String(500), nullable=False, comment='密码')
    role_id = Column(ForeignKey('role.id'), index=True)
    role = relationship('Role')
    update_time = Column(DATETIME, server_default=func.now(), onupdate=func.now(), nullable=False, comment='更新时间')
    create_time = Column(DATETIME, server_default=func.now(), nullable=False, comment='创建时间')

    __table_args__ = ({'comment': '用户'})


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

