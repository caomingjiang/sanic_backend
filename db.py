from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Integer, String, Float, ForeignKey, Column, Boolean, Index
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


class ChassisBase(Base):
    __tablename__ = 'chassis_base'

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    radiation_sound = Column(Float, comment='轮胎-胎面辐射声（轮胎选型）')
    peak_frequency = Column(Float, comment='轮胎-力传递峰值频率')
    force_transfer = Column(Float, comment='轮胎-力传递峰值')
    stability_performance = Column(Float, comment='轮胎-操稳性能')
    durability = Column(Float, comment='轮胎-耐久性能')
    rim_stiffness_a = Column(Float, comment='轮辋刚度-16-17’')
    rim_stiffness_b = Column(Float, comment='轮辋刚度-18-19’')
    full_bend_mode = Column(Float, comment='前副车架（自由-自由）-全副车架(bend)模态')
    half_bend_mode = Column(Float, comment='前副车架（自由-自由）-半副车架(bend)模态')
    torsion_beam = Column(Float, comment='后副车架（自由-自由）-类型一：扭转梁(bend)模态')
    multi_link = Column(Float, comment='后副车架（自由-自由）-类型二：多连杆(横梁弯曲)模态')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        {'comment': '底盘-基本信息'}
    )

    def to_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
            if c.name not in ['update_time', 'create_time', 'id']
        }


class ChassisDetail(Base):
    __tablename__ = 'chassis_detail'

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    handling_x = Column(Float, comment='前下摆臂handling衬套-X向静刚度')
    handling_y = Column(Float, comment='前下摆臂handling衬套-Y向静刚度')
    handling_z = Column(Float, comment='前下摆臂handling衬套-Z向静刚度')
    handling_stability = Column(Float, comment='前下摆臂handling衬套-操稳性能')
    handling_durability = Column(Float, comment='前下摆臂handling衬套-耐久性能')
    ride_x = Column(Float, comment='前下摆臂ride衬套-X向静刚度')
    ride_y = Column(Float, comment='前下摆臂ride衬套-Y向静刚度')
    ride_z = Column(Float, comment='前下摆臂ride衬套-Z向静刚度')
    ride_stability = Column(Float, comment='前下摆臂ride衬套-操稳性能')
    ride_durability = Column(Float, comment='前下摆臂ride衬套-耐久性能')
    front_subframe_x = Column(Float, comment='后副车架前衬套-X向静刚度')
    front_subframe_y = Column(Float, comment='后副车架前衬套-Y向静刚度')
    front_subframe_z = Column(Float, comment='后副车架前衬套-Z向静刚度')
    front_subframe_stability = Column(Float, comment='后副车架前衬套-操稳性能')
    front_subframe_durability = Column(Float, comment='后副车架前衬套-耐久性能')
    backend_subframe_x = Column(Float, comment='后副车架后衬套-X向静刚度')
    backend_subframe_y = Column(Float, comment='后副车架后衬套-Y向静刚度')
    backend_subframe_z = Column(Float, comment='后副车架后衬套-Z向静刚度')
    backend_subframe_stability = Column(Float, comment='后副车架后衬套-操稳性能')
    backend_subframe_durability = Column(Float, comment='后副车架后衬套-耐久性能')
    blade_arm_x = Column(Float, comment='刀锋臂衬套-X向静刚度')
    blade_arm_y = Column(Float, comment='刀锋臂衬套-Y向静刚度')
    blade_arm_z = Column(Float, comment='刀锋臂衬套-Z向静刚度')
    blade_arm_stability = Column(Float, comment='刀锋臂衬套-操稳性能')
    blade_arm_durability = Column(Float, comment='刀锋臂衬套-耐久性能')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        {'comment': '底盘-详细信息'}
    )

    def to_dict(self):
        return {
            c.name: getattr(self, c.name) for c in self.__table__.columns
            if c.name not in ['update_time', 'create_time', 'id']
        }


try:
    Base.metadata.create_all(engine)
except Exception as e:
    pass
Session = sessionmaker(bind=engine)

