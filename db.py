from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine, Integer, String, Float, ForeignKey, Column, Boolean, Index
from sqlalchemy.dialects.mysql import DATETIME, INTEGER, LONGTEXT, SMALLINT, TINYINT
from sqlalchemy_utils import ChoiceType
from confs.config import MYSQL_CONFIG
from enum import Enum, unique


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
    DATA_TYPE_CHOICES = (
        ('radiation_sound', '轮胎 -- 胎面辐射声（轮胎选型）'),
        ('peak_frequency', '轮胎 -- 力传递峰值频率'),
        ('force_transfer', '轮胎 -- 力传递峰值'),
        ('stability_performance', '轮胎 -- 操稳性能'),
        ('durability', '轮胎 -- 耐久性能'),
        ('rim_stiffness_a', '轮辋刚度 -- 16-17’'),
        ('rim_stiffness_b', '轮辋刚度 -- 18-19’'),
        ('full_bend_mode', '前副车架（自由-自由） -- 全副车架(bend)模态'),
        ('half_bend_mode', '前副车架（自由-自由） -- 半副车架(bend)模态'),
        ('torsion_beam', '后副车架（自由-自由） -- 类型一：扭转梁(bend)模态'),
        ('multi_link', '后副车架（自由-自由） -- 类型二：多连杆(横梁弯曲)模态'),
        ('tire_score', '轮胎总分')
    )

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    data_type = Column(ChoiceType(DATA_TYPE_CHOICES, String(128)), comment="数据类型")
    value = Column(Float(precision='10,2'), comment="值")
    score = Column(Float(precision='10,2'), comment="分值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        {'comment': '底盘-基本信息'}
    )


class ChassisDetail(Base):
    __tablename__ = 'chassis_detail'
    DATA_TYPE_CHOICES = (
        ('handling_x', '前下摆臂handling衬套 -- X向静刚度'),
        ('handling_y', '前下摆臂handling衬套 -- Y向静刚度'),
        ('handling_z', '前下摆臂handling衬套 -- Z向静刚度'),
        ('handling_stability', '前下摆臂handling衬套 -- 操稳性能'),
        ('handling_durability', '前下摆臂handling衬套 -- 耐久性能'),
        ('ride_x', '前下摆臂ride衬套 -- X向静刚度'),
        ('ride_y', '前下摆臂ride衬套 -- Y向静刚度'),
        ('ride_z', '前下摆臂ride衬套 -- Z向静刚度'),
        ('ride_stability', '前下摆臂ride衬套 -- 操稳性能'),
        ('ride_durability', '前下摆臂ride衬套 -- 耐久性能'),
        ('front_subframe_x', '后副车架前衬套 -- X向静刚度'),
        ('front_subframe_y', '后副车架前衬套 -- Y向静刚度'),
        ('front_subframe_z', '后副车架前衬套 -- Z向静刚度'),
        ('front_subframe_stability', '后副车架前衬套 -- 操稳性能'),
        ('front_subframe_durability', '后副车架前衬套 -- 耐久性能'),
        ('backend_subframe_x', '后副车架后衬套 -- X向静刚度'),
        ('backend_subframe_y', '后副车架后衬套 -- Y向静刚度'),
        ('backend_subframe_z', '后副车架后衬套 -- Z向静刚度'),
        ('backend_subframe_stability', '后副车架后衬套 -- 操稳性能'),
        ('backend_subframe_durability', '后副车架后衬套 -- 耐久性能'),
        ('blade_arm_x', '刀锋臂衬套 -- X向静刚度'),
        ('blade_arm_y', '刀锋臂衬套 -- Y向静刚度'),
        ('blade_arm_z', '刀锋臂衬套 -- Z向静刚度'),
        ('blade_arm_stability', '刀锋臂衬套 -- 操稳性能'),
        ('blade_arm_durability', '刀锋臂衬套 -- 耐久性能')
    )

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    data_type = Column(ChoiceType(DATA_TYPE_CHOICES, String(128)), comment="数据类型")
    molecule = Column(Float(precision='10,2'), comment="数据输入-分子")
    denominator = Column(Float(precision='10,2'), comment="数据输入-分母")
    stiffness_ratio = Column(Float(precision='10,2'), comment="刚度比，数据输入-分子/数据输入-分母")
    score = Column(Float(precision='10,2'), comment="分值")
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


class ModalMap(Base):
    __tablename__ = 'd_modal_map'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    value_range = Column(String(128), nullable=False, comment='值范围')
    front_tire = Column(Float(precision='10,2'), comment='前悬-轮胎')
    front_power_train = Column(Float(precision='10,2'), comment='前悬-动力总成')
    front_fsubframe = Column(Float(precision='10,2'), comment='前悬-前副车架')
    front_fdc_arm = Column(Float(precision='10,2'), comment='前悬-前下控制臂')
    front_fspring = Column(Float(precision='10,2'), comment='前悬-前弹簧')
    front_fork_arm = Column(Float(precision='10,2'), comment='前悬-上叉臂')
    front_fsta_bar = Column(Float(precision='10,2'), comment='前悬-前稳定杆')
    backend_bsubframe = Column(Float(precision='10,2'), comment='后悬-后副车架')
    backend_bspring = Column(Float(precision='10,2'), comment='后悬-后弹簧')
    backend_blade_arm = Column(Float(precision='10,2'), comment='后悬-刀锋臂')
    backend_fdc_arm = Column(Float(precision='10,2'), comment='后悬-前下控制臂')
    backend_bdc_arm = Column(Float(precision='10,2'), comment='后悬-后下控制臂')
    backend_fuc_arm = Column(Float(precision='10,2'), comment='后悬-前上控制臂')
    backend_buc_arm = Column(Float(precision='10,2'), comment='后悬-后上控制臂')
    backend_bsta_bar = Column(Float(precision='10,2'), comment='后悬-后稳定杆')
    body_fcm_skylight = Column(Float(precision='10,2'), comment='车身-天窗前横梁')
    body_rcm_roof = Column(Float(precision='10,2'), comment='车身-顶棚后横梁')
    body_f_windshield = Column(Float(precision='10,2'), comment='车身-前风挡')
    body_skylight = Column(Float(precision='10,2'), comment='车身-天窗')
    body_b_windshield = Column(Float(precision='10,2'), comment='车身-后风挡')
    body_f_floor = Column(Float(precision='10,2'), comment='车身-前地板')
    body_b_floor = Column(Float(precision='10,2'), comment='车身-后地板')
    body_coat_rack = Column(Float(precision='10,2'), comment='车身-衣帽架')
    body_swh_slot = Column(Float(precision='10,2'), comment='车身-备胎槽')
    body_vocal_cavity = Column(Float(precision='10,2'), comment='车身-声腔')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_value_range', 'car_info_id', 'value_range', unique=True),
        {'comment': 'ModalMap表'}
    )


class Dstiff(Base):
    __tablename__ = 'd_dstiff'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    fsb_ap_x = Column(Float(precision='10,2'), comment='前悬左塔座接附点X')
    fsb_ap_y = Column(Float(precision='10,2'), comment='前悬左塔座接附点Y')
    fsb_ap_z = Column(Float(precision='10,2'), comment='前悬左塔座接附点Z')
    fslca_fap_x = Column(Float(precision='10,2'), comment='前悬左控制臂前接附点X')
    fslca_fap_y = Column(Float(precision='10,2'), comment='前悬左控制臂前接附点Y')
    fslca_fap_z = Column(Float(precision='10,2'), comment='前悬左控制臂前接附点Z')
    fslca_rap_x = Column(Float(precision='10,2'), comment='前悬左控制臂后接附点X')
    fslca_rap_y = Column(Float(precision='10,2'), comment='前悬左控制臂后接附点Y')
    fslca_rap_z = Column(Float(precision='10,2'), comment='前悬左控制臂后接附点Z')
    lba_ap_x = Column(Float(precision='10,2'), comment='左刀锋臂接附点X')
    lba_ap_y = Column(Float(precision='10,2'), comment='左刀锋臂接附点Y')
    lba_ap_z = Column(Float(precision='10,2'), comment='左刀锋臂接附点Z')
    rslsa_ap_x = Column(Float(precision='10,2'), comment='后悬左减震接附点X')
    rslsa_ap_y = Column(Float(precision='10,2'), comment='后悬左减震接附点Y')
    rslsa_ap_z = Column(Float(precision='10,2'), comment='后悬左减震接附点Z')
    rsls_ap_x = Column(Float(precision='10,2'), comment='后悬左弹簧接附点X')
    rsls_ap_y = Column(Float(precision='10,2'), comment='后悬左弹簧接附点Y')
    rsls_ap_z = Column(Float(precision='10,2'), comment='后悬左弹簧接附点Z')
    rsluca_ap_x = Column(Float(precision='10,2'), comment='后悬左上控制臂接附点X')
    rsluca_ap_y = Column(Float(precision='10,2'), comment='后悬左上控制臂接附点Y')
    rsluca_ap_z = Column(Float(precision='10,2'), comment='后悬左上控制臂接附点Z')
    rslll_ap_x = Column(Float(precision='10,2'), comment='后悬左下拉杆接附点X')
    rslll_ap_y = Column(Float(precision='10,2'), comment='后悬左下拉杆接附点Y')
    rslll_ap_z = Column(Float(precision='10,2'), comment='后悬左下拉杆接附点Z')
    rslsai_ap_x = Column(Float(precision='10,2'), comment='后悬左弹簧臂内接附点X')
    rslsai_ap_y = Column(Float(precision='10,2'), comment='后悬左弹簧臂内接附点Y')
    rslsai_ap_z = Column(Float(precision='10,2'), comment='后悬左弹簧臂内接附点Z')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': 'Dstiff表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for column in cls.__table__.columns:
            comment = getattr(cls, column.name).comment
            if comment:
                ret_data[comment] = column.name
        return ret_data


class ColorMapDstiff(Base):
    __tablename__ = 'c_color_map_dstiff'

    DATA_TYPE_ITEMS = [
        ('frequency_range', '频率范围'),
        ('fsb_ap_x', '前悬左塔座接附点X'),
        ('fsb_ap_y', '前悬左塔座接附点Y'),
        ('fsb_ap_z', '前悬左塔座接附点Z'),
        ('fslca_fap_x', '前悬左控制臂前接附点X'),
        ('fslca_fap_y', '前悬左控制臂前接附点Y'),
        ('fslca_fap_z', '前悬左控制臂前接附点Z'),
        ('fslca_rap_x', '前悬左控制臂后接附点X'),
        ('fslca_rap_y', '前悬左控制臂后接附点Y'),
        ('fslca_rap_z', '前悬左控制臂后接附点Z'),
        ('lba_ap_x', '左刀锋臂接附点X'),
        ('lba_ap_y', '左刀锋臂接附点Y'),
        ('lba_ap_z', '左刀锋臂接附点Z'),
        ('rslsa_ap_x', '后悬左减震接附点X'),
        ('rslsa_ap_y', '后悬左减震接附点Y'),
        ('rslsa_ap_z', '后悬左减震接附点Z'),
        ('rsls_ap_x', '后悬左弹簧接附点X'),
        ('rsls_ap_y', '后悬左弹簧接附点Y'),
        ('rsls_ap_z', '后悬左弹簧接附点Z'),
        ('rsluca_ap_x', '后悬左上控制臂接附点X'),
        ('rsluca_ap_y', '后悬左上控制臂接附点Y'),
        ('rsluca_ap_z', '后悬左上控制臂接附点Z'),
        ('rslll_ap_x', '后悬左下拉杆接附点X'),
        ('rslll_ap_y', '后悬左下拉杆接附点Y'),
        ('rslll_ap_z', '后悬左下拉杆接附点Z'),
        ('rslsai_ap_x', '后悬左弹簧臂内接附点X'),
        ('rslsai_ap_y', '后悬左弹簧臂内接附点Y'),
        ('rslsai_ap_z', '后悬左弹簧臂内接附点Z'),
    ]

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    frequency_range = Column(String(128), nullable=False, comment='频率范围')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    value = Column(Float, nullable=False, comment="权重值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency_range', 'car_info_id', 'frequency_range', 'data_type', unique=True),
        {'comment': 'ColorMap Dstiff表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for data_type, type_name in cls.DATA_TYPE_ITEMS:
            ret_data[type_name] = data_type
        return ret_data


class NtfDr(Base):
    __tablename__ = 'd_ntf_dr'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    fslftt_driver_x = Column(Float(precision='10,2'), comment='前悬左前塔座到DriverX')
    fslftt_driver_y = Column(Float(precision='10,2'), comment='前悬左前塔座到DriverY')
    fslftt_driver_z = Column(Float(precision='10,2'), comment='前悬左前塔座到DriverZ')
    fslfca_driver_x = Column(Float(precision='10,2'), comment='前悬左前控制臂到DriverX')
    fslfca_driver_y = Column(Float(precision='10,2'), comment='前悬左前控制臂到DriverY')
    fslfca_driver_z = Column(Float(precision='10,2'), comment='前悬左前控制臂到DriverZ')
    fslrca_driver_x = Column(Float(precision='10,2'), comment='前悬左后控制臂到DriverX')
    fslrca_driver_y = Column(Float(precision='10,2'), comment='前悬左后控制臂到DriverY')
    fslrca_driver_z = Column(Float(precision='10,2'), comment='前悬左后控制臂到DriverZ')
    lba_driver_x = Column(Float(precision='10,2'), comment='左刀锋臂到DriverX')
    lba_driver_y = Column(Float(precision='10,2'), comment='左刀锋臂到DriverY')
    lba_driver_z = Column(Float(precision='10,2'), comment='左刀锋臂到DriverZ')
    rslrsa_diver_x = Column(Float(precision='10,2'), comment='后悬左后减振器到DriverX')
    rslrsa_diver_y = Column(Float(precision='10,2'), comment='后悬左后减振器到DriverY')
    rslrsa_diver_z = Column(Float(precision='10,2'), comment='后悬左后减振器到DriverZ')
    rslrss_driver_x = Column(Float(precision='10,2'), comment='后悬左后弹簧座到DriverX')
    rslrss_driver_y = Column(Float(precision='10,2'), comment='后悬左后弹簧座到DriverY')
    rslrss_driver_z = Column(Float(precision='10,2'), comment='后悬左后弹簧座到DriverZ')
    rsulca_driver_x = Column(Float(precision='10,2'), comment='后悬左上控制臂到DriverX')
    rsulca_driver_y = Column(Float(precision='10,2'), comment='后悬左上控制臂到DriverY')
    rsulca_driver_z = Column(Float(precision='10,2'), comment='后悬左上控制臂到DriverZ')
    rlll_driver_x = Column(Float(precision='10,2'), comment='后悬左下拉杆到DriverX')
    rlll_driver_y = Column(Float(precision='10,2'), comment='后悬左下拉杆到DriverY')
    rlll_driver_z = Column(Float(precision='10,2'), comment='后悬左下拉杆到DriverZ')
    rslsa_driver_x = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到DriverX')
    rslsa_driver_y = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到DriverY')
    rslsa_driver_z = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到DriverZ')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': 'NtfDr表'}
    )


class ColorMapNtfDr(Base):
    __tablename__ = 'c_color_map_ntf_dr'

    DATA_TYPE_ITEMS = [
        ('frequency_range', '频率范围'),
        ('fslftt_driver_x', '前悬左前塔座到DriverX'),
        ('fslftt_driver_y', '前悬左前塔座到DriverY'),
        ('fslftt_driver_z', '前悬左前塔座到DriverZ'),
        ('fslfca_driver_x', '前悬左前控制臂到DriverX'),
        ('fslfca_driver_y', '前悬左前控制臂到DriverY'),
        ('fslfca_driver_z', '前悬左前控制臂到DriverZ'),
        ('fslrca_driver_x', '前悬左后控制臂到DriverX'),
        ('fslrca_driver_y', '前悬左后控制臂到DriverY'),
        ('fslrca_driver_z', '前悬左后控制臂到DriverZ'),
        ('lba_driver_x', '左刀锋臂到DriverX'),
        ('lba_driver_y', '左刀锋臂到DriverY'),
        ('lba_driver_z', '左刀锋臂到DriverZ'),
        ('rslrsa_diver_x', '后悬左后减振器到DriverX'),
        ('rslrsa_diver_y', '后悬左后减振器到DriverY'),
        ('rslrsa_diver_z', '后悬左后减振器到DriverZ'),
        ('rslrss_driver_x', '后悬左后弹簧座到DriverX'),
        ('rslrss_driver_y', '后悬左后弹簧座到DriverY'),
        ('rslrss_driver_z', '后悬左后弹簧座到DriverZ'),
        ('rsulca_driver_x', '后悬左上控制臂到DriverX'),
        ('rsulca_driver_y', '后悬左上控制臂到DriverY'),
        ('rsulca_driver_z', '后悬左上控制臂到DriverZ'),
        ('rlll_driver_x', '后悬左下拉杆到DriverX'),
        ('rlll_driver_y', '后悬左下拉杆到DriverY'),
        ('rlll_driver_z', '后悬左下拉杆到DriverZ'),
        ('rslsa_driver_x', '后悬左弹簧托臂到DriverX'),
        ('rslsa_driver_y', '后悬左弹簧托臂到DriverY'),
        ('rslsa_driver_z', '后悬左弹簧托臂到DriverZ'),
    ]

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    frequency_range = Column(String(128), nullable=False, comment='频率范围')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    value = Column(Float, nullable=False, comment="权重值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency_range', 'car_info_id', 'frequency_range', 'data_type', unique=True),
        {'comment': 'ColorMap NtfDr表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for data_type, type_name in cls.DATA_TYPE_ITEMS:
            ret_data[type_name] = data_type
        return ret_data


class NtfRr(Base):
    __tablename__ = 'd_ntf_rr'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    fslft_passenger_x = Column(Float(precision='10,2'), comment='前悬左前塔座到PassengerX')
    fslft_passenger_y = Column(Float(precision='10,2'), comment='前悬左前塔座到PassengerY')
    fslft_passenger_z = Column(Float(precision='10,2'), comment='前悬左前塔座到PassengerZ')
    fslfca_passenger_x = Column(Float(precision='10,2'), comment='前悬左前控制臂到PassengerX')
    fslfca_passenger_y = Column(Float(precision='10,2'), comment='前悬左前控制臂到PassengerY')
    fslfca_passenger_z = Column(Float(precision='10,2'), comment='前悬左前控制臂到PassengerZ')
    fslrca_passenger_x = Column(Float(precision='10,2'), comment='前悬左后控制臂到PassengerX')
    fslrca_passenger_y = Column(Float(precision='10,2'), comment='前悬左后控制臂到PassengerY')
    fslrca_passenger_z = Column(Float(precision='10,2'), comment='前悬左后控制臂到PassengerZ')
    lba_passenger_x = Column(Float(precision='10,2'), comment='左刀锋臂到PassengerX')
    lba_passenger_y = Column(Float(precision='10,2'), comment='左刀锋臂到PassengerY')
    lba_passenger_z = Column(Float(precision='10,2'), comment='左刀锋臂到PassengerZ')
    rslrsa_passenger_x = Column(Float(precision='10,2'), comment='后悬左后减振器到PassengerX')
    rslrsa_passenger_y = Column(Float(precision='10,2'), comment='后悬左后减振器到PassengerY')
    rslrsa_passenger_z = Column(Float(precision='10,2'), comment='后悬左后减振器到PassengerZ')
    rslrss_passenger_x = Column(Float(precision='10,2'), comment='后悬左后弹簧座到PassengerX')
    rslrss_passenger_y = Column(Float(precision='10,2'), comment='后悬左后弹簧座到PassengerY')
    rslrss_passenger_z = Column(Float(precision='10,2'), comment='后悬左后弹簧座到PassengerZ')
    rsluca_passenger_x = Column(Float(precision='10,2'), comment='后悬左上控制臂到PassengerX')
    rsluca_passenger_y = Column(Float(precision='10,2'), comment='后悬左上控制臂到PassengerY')
    rsluca_passenger_z = Column(Float(precision='10,2'), comment='后悬左上控制臂到PassengerZ')
    rlll_passenger_x = Column(Float(precision='10,2'), comment='后悬左下拉杆到PassengerX')
    rlll_passenger_y = Column(Float(precision='10,2'), comment='后悬左下拉杆到PassengerY')
    rlll_passenger_z = Column(Float(precision='10,2'), comment='后悬左下拉杆到PassengerZ')
    rslsa_passenger_x = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到PassengerX')
    rslsa_passenger_y = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到PassengerY')
    rslsa_passenger_z = Column(Float(precision='10,2'), comment='后悬左弹簧托臂到PassengerZ')

    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': 'NtfRr表'}
    )


class ColorMapNtfRr(Base):
    __tablename__ = 'c_color_map_ntf_rr'

    DATA_TYPE_ITEMS = [
        ('frequency_range', '频率范围'),
        ('fslft_passenger_x', '前悬左前塔座到PassengerX'),
        ('fslft_passenger_y', '前悬左前塔座到PassengerY'),
        ('fslft_passenger_z', '前悬左前塔座到PassengerZ'),
        ('fslfca_passenger_x', '前悬左前控制臂到PassengerX'),
        ('fslfca_passenger_y', '前悬左前控制臂到PassengerY'),
        ('fslfca_passenger_z', '前悬左前控制臂到PassengerZ'),
        ('fslrca_passenger_x', '前悬左后控制臂到PassengerX'),
        ('fslrca_passenger_y', '前悬左后控制臂到PassengerY'),
        ('fslrca_passenger_z', '前悬左后控制臂到PassengerZ'),
        ('lba_passenger_x', '左刀锋臂到PassengerX'),
        ('lba_passenger_y', '左刀锋臂到PassengerY'),
        ('lba_passenger_z', '左刀锋臂到PassengerZ'),
        ('rslrsa_passenger_x', '后悬左后减振器到PassengerX'),
        ('rslrsa_passenger_y', '后悬左后减振器到PassengerY'),
        ('rslrsa_passenger_z', '后悬左后减振器到PassengerZ'),
        ('rslrss_passenger_x', '后悬左后弹簧座到PassengerX'),
        ('rslrss_passenger_y', '后悬左后弹簧座到PassengerY'),
        ('rslrss_passenger_z', '后悬左后弹簧座到PassengerZ'),
        ('rsluca_passenger_x', '后悬左上控制臂到PassengerX'),
        ('rsluca_passenger_y', '后悬左上控制臂到PassengerY'),
        ('rsluca_passenger_z', '后悬左上控制臂到PassengerZ'),
        ('rlll_passenger_x', '后悬左下拉杆到PassengerX'),
        ('rlll_passenger_y', '后悬左下拉杆到PassengerY'),
        ('rlll_passenger_z', '后悬左下拉杆到PassengerZ'),
        ('rslsa_passenger_x', '后悬左弹簧托臂到PassengerX'),
        ('rslsa_passenger_y', '后悬左弹簧托臂到PassengerY'),
        ('rslsa_passenger_z', '后悬左弹簧托臂到PassengerZ')
    ]

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    frequency_range = Column(String(128), nullable=False, comment='频率范围')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    value = Column(Float, nullable=False, comment="权重值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency_range', 'car_info_id', 'frequency_range', 'data_type', unique=True),
        {'comment': 'ColorMap NtfRr表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for data_type, type_name in cls.DATA_TYPE_ITEMS:
            ret_data[type_name] = data_type
        return ret_data


class SpindleNtfDr(Base):
    __tablename__ = 'd_spindle_ntf_dr'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    lfwc_driver_x = Column(Float(precision='10,2'), comment='左前轮心_DriverX')
    lfwc_driver_y = Column(Float(precision='10,2'), comment='左前轮心_DriverY')
    lfwc_driver_z = Column(Float(precision='10,2'), comment='左前轮心_DriverZ')
    rfwc_driver_x = Column(Float(precision='10,2'), comment='右前轮心_DriverX')
    rfwc_driver_y = Column(Float(precision='10,2'), comment='右前轮心_DriverY')
    rfwc_driver_z = Column(Float(precision='10,2'), comment='右前轮心_DriverZ')
    lrwh_driver_x = Column(Float(precision='10,2'), comment='左后轮心_DriverX')
    lrwh_driver_y = Column(Float(precision='10,2'), comment='左后轮心_DriverY')
    lrwh_driver_z = Column(Float(precision='10,2'), comment='左后轮心_DriverZ')
    rrwc_driver_x = Column(Float(precision='10,2'), comment='右后轮心_DriverX')
    rrwc_driver_y = Column(Float(precision='10,2'), comment='右后轮心_DriverY')
    rrwc_driver_z = Column(Float(precision='10,2'), comment='右后轮心_DriverZ')

    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': 'SpindleNtfDr表'}
    )


class ColorMapSpindleNtfDr(Base):
    __tablename__ = 'c_color_map_spindle_ntf_dr'

    DATA_TYPE_ITEMS = [
        ('frequency_range', '频率范围'),
        ('lfwc_driver_x', '左前轮心_DriverX'),
        ('lfwc_driver_y', '左前轮心_DriverY'),
        ('lfwc_driver_z', '左前轮心_DriverZ'),
        ('rfwc_driver_x', '右前轮心_DriverX'),
        ('rfwc_driver_y', '右前轮心_DriverY'),
        ('rfwc_driver_z', '右前轮心_DriverZ'),
        ('lrwh_driver_x', '左后轮心_DriverX'),
        ('lrwh_driver_y', '左后轮心_DriverY'),
        ('lrwh_driver_z', '左后轮心_DriverZ'),
        ('rrwc_driver_x', '右后轮心_DriverX'),
        ('rrwc_driver_y', '右后轮心_DriverY'),
        ('rrwc_driver_z', '右后轮心_DriverZ')
    ]

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    frequency_range = Column(String(128), nullable=False, comment='频率范围')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    value = Column(Float, nullable=False, comment="权重值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency_range', 'car_info_id', 'frequency_range', 'data_type', unique=True),
        {'comment': 'ColorMap SpindleNtfDr表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for data_type, type_name in cls.DATA_TYPE_ITEMS:
            ret_data[type_name] = data_type
        return ret_data


class SpindleNtfRr(Base):
    __tablename__ = 'd_spindle_ntf_rr'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    lfwc_rrx = Column(Float(precision='10,2'), comment='左前轮心_RRX')
    lfwc_rry = Column(Float(precision='10,2'), comment='左前轮心_RRY')
    lfwc_rrz = Column(Float(precision='10,2'), comment='左前轮心_RRZ')
    rfwc_rrx = Column(Float(precision='10,2'), comment='右前轮心_RRX')
    rfwc_rry = Column(Float(precision='10,2'), comment='右前轮心_RRY')
    rfwc_rrz = Column(Float(precision='10,2'), comment='右前轮心_RRZ')
    lrwh_rrx = Column(Float(precision='10,2'), comment='左后轮心_RRX')
    lrwh_rry = Column(Float(precision='10,2'), comment='左后轮心_RRY')
    lrwh_rrz = Column(Float(precision='10,2'), comment='左后轮心_RRZ')
    rrwc_rrx = Column(Float(precision='10,2'), comment='右后轮心_RRX')
    rrwc_rry = Column(Float(precision='10,2'), comment='右后轮心_RRY')
    rrwc_rrz = Column(Float(precision='10,2'), comment='右后轮心_RRZ')

    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': 'SpindleNtfRr表'}
    )


class ColorMapSpindleNtfRr(Base):
    __tablename__ = 'c_color_map_spindle_ntf_rr'

    DATA_TYPE_ITEMS = [
        ('frequency_range', '频率范围'),
        ('lfwc_rrx', '左前轮心_RRX'),
        ('lfwc_rry', '左前轮心_RRY'),
        ('lfwc_rrz', '左前轮心_RRZ'),
        ('rfwc_rrx', '右前轮心_RRX'),
        ('rfwc_rry', '右前轮心_RRY'),
        ('rfwc_rrz', '右前轮心_RRZ'),
        ('lrwh_rrx', '左后轮心_RRX'),
        ('lrwh_rry', '左后轮心_RRY'),
        ('lrwh_rrz', '左后轮心_RRZ'),
        ('rrwc_rrx', '右后轮心_RRX'),
        ('rrwc_rry', '右后轮心_RRY'),
        ('rrwc_rrz', '右后轮心_RRZ')
    ]

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    frequency_range = Column(String(128), nullable=False, comment='频率范围')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    value = Column(Float, nullable=False, comment="权重值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency_range', 'car_info_id', 'frequency_range', 'data_type', unique=True),
        {'comment': 'ColorMap SpindleNtfRr表'}
    )

    @classmethod
    def comment_dic(cls):
        ret_data = {}
        for data_type, type_name in cls.DATA_TYPE_ITEMS:
            ret_data[type_name] = data_type
        return ret_data


class ActualTestData(Base):
    __tablename__ = 'd_actual_test_data'
    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')

    frequency = Column(Float, nullable=False, comment='频率')
    act_driver = Column(Float(precision='10,2'), comment='实测_Driver')
    act_rr_passenger = Column(Float(precision='10,2'), comment='实测_RR-Passenger')

    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_frequency', 'car_info_id', 'frequency', unique=True),
        {'comment': '实测数据表'}
    )


class CarExcelData(Base):
    __tablename__ = 'car_excel_data'
    DATA_TYPE_ITEMS = (
        ('modal_map', "ModalMap表"),
        ('dstiff', "Dstiff表"),
        ('ntf_dr', "NtfDr表"),
        ('ntf_rr', "NtfRr表"),
        ('spindle_ntf_dr', "SpindleNtfDr表"),
        ('spindle_ntf_rr', "SpindleNtfRr表"),
        ('actual_test_data', "实测数据表"),
    )

    id = Column(INTEGER(11), primary_key=True)
    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    data_type = Column(ChoiceType(DATA_TYPE_ITEMS, String(50)), nullable=False, comment='数据类型')
    excel_name = Column(String(128), comment='excel文件名称')
    excel_path = Column(String(250), comment='excel文件路径')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        Index('car_info_data_type', 'car_info_id', 'data_type', unique=True),
        {'comment': '车型excel对应表'}
    )


class CarBody(Base):
    __tablename__ = 'car_body'
    DATA_TYPE_CHOICES = (
        ('biw_gtmf', '白车身 -- 全局扭转模态频率'),
        ('biw_gbmf', '白车身 -- 全局弯曲模态频率'),
        ('cring_vc', 'C ring -- Visual Check'),
        ('fwall_lps', '前围 -- 大板刚度'),
        ('no1_beam_vc', '一号梁 -- Visual Check'),
        ('floor_lps', '地板 -- 大板刚度'),
        ('fawsp_vc', '地板无支撑板面积 -- Visual Check'),
        ('swcf_lps', '备胎舱地板 -- 大板刚度'),
        ('dorpfswc_vc', '备胎舱加强板设计 -- Visual Check'),
        ('ceiling_lps', '顶棚 -- 大板刚度'),
        ('ceiling_st_vc', '顶棚结构 -- Visual Check'),
        ('lwhip_lps', '左轮罩内板 -- 大板刚度'),
        ('rsarp_vc', '后减震器加强板 -- Visual Check'),
        ('rwhip_lps', '右轮罩内板 -- 大板刚度'),
        ('rsop_lps', '后侧围外板 -- 大板刚度'),
        ('coat_rack_lps', '衣帽架 -- 大板刚度'),
        ('flume_lps', '落水槽 -- 大板刚度'),
        ('dotsotwt_vc', '落水槽支架设计 -- Visual Check'),
    )

    id = Column(INTEGER(11), primary_key=True)

    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    data_type = Column(ChoiceType(DATA_TYPE_CHOICES, String(128)), comment="数据类型")
    value = Column(String(128), comment="值")
    score = Column(Float(precision='10,2'), comment="分值")
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        {'comment': '单值数据-车身'}
    )


class DesignLibrary(Base):
    __tablename__ = 'design_library'
    DATA_TYPE_CHOICES = (
        ('cring_vc', 'C ring'),
        ('no1_beam_vc', '一号梁'),
        ('fawsp_vc', '地板无支撑板面积'),
        ('dorpfswc_vc', '备胎舱加强板设计'),
        ('ceiling_st_vc', '顶棚结构'),
        ('rsarp_vc', '后减震器加强板'),
        ('dotsotwt_vc', '落水槽支架设计'),
        ('front_subframe', '前副车架'),
        ('backend_subframe', '后副车架'),
    )

    id = Column(INTEGER(11), primary_key=True)
    car_info_id = Column(ForeignKey('car_info.id'), index=True, nullable=False, comment="车型")
    car_info = relationship('CarInfo')
    data_type = Column(ChoiceType(DATA_TYPE_CHOICES, String(128)), comment="数据类型")
    poor_design_1 = Column(String(250), comment='较差设计1')
    poor_design_2 = Column(String(250), comment='较差设计2')
    low_cost_scheme = Column(String(250), comment='低成本优化方案')
    optimal_scheme_1 = Column(String(250), comment='最优方案1')
    optimal_scheme_2 = Column(String(250), comment='最优方案2')
    update_time = Column(DATETIME, nullable=False, comment='更新时间')
    create_time = Column(DATETIME, nullable=False, comment='创建时间')

    __table_args__ = (
        {'comment': '专家设定-设计参照库'}
    )


try:
    Base.metadata.create_all(engine)
except Exception as e:
    pass
Session = sessionmaker(bind=engine)

