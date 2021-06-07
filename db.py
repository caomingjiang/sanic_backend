from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Integer, String, ForeignKey, Column, Boolean, Index
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
    description = Column(LONGTEXT, comment='描述')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

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
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = ({'comment': '用户'})


class DevStage(Base):
    __tablename__ = 'dev_stage'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(128), nullable=False, unique=True, comment='阶段名称')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = ({'comment': '开发阶段'})


class CarInfo(Base):
    """
    车型信息
    """
    __tablename__ = 'car_info'

    id = Column(INTEGER(11), primary_key=True)
    car_name = Column(String(128), nullable=False, unique=True, comment='车型名称')

    dev_stage_id = Column(ForeignKey('dev_stage.id'), index=True, nullable=False, comment="当前开发阶段")
    dev_stage = relationship('DevStage')

    car_body = Column(String(128), nullable=False, comment='车身形式')
    front_suspension = Column(String(128), nullable=False, comment='前悬形式')
    front_subframe = Column(String(128), nullable=False, comment='前副车架')
    backend_suspension = Column(String(128), nullable=False, comment='后悬形式')
    backend_subframe = Column(String(128), nullable=False, comment='后副车架')
    is_dev = Column(Boolean, nullable=False, default=False, comment='是否开发中')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = ({'comment': '用户'})


class CarTestInfo(Base):
    __tablename__ = 'car_test_info'

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    dev_stage_id = Column(ForeignKey('dev_stage.id'), index=True, nullable=False, comment="开发阶段")
    dev_stage = relationship('DevStage')

    data_source = Column(String(128), comment='数据来源')
    test_time = Column(DATETIME, comment='测试/分析时间')
    test_user = Column(String(128), comment='测试/分析人')

    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_dev_stage_uniq', 'car_info_id', 'dev_stage_id', unique=True),
        {'comment': '车型 测试/分析 历史信息'}
    )


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

