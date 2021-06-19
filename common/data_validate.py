from pydantic import BaseModel, StrictInt, StrictStr, Field, validator, constr
from typing import Optional, List
from typing_extensions import Literal
import re


class LoginValidate(BaseModel):
    account: StrictStr = Field(description="账号")
    password: StrictStr = Field(description="密码")


class UpdateUserPassword(BaseModel):
    old_pwd: StrictStr = Field(description="原密码")
    new_pwd: StrictStr = Field(description="新密码")


class AddCarInfo(BaseModel):
    car_name: constr(min_length=1) = Field(description="车型名称")
    dev_stage_id: StrictInt = Field(description="开发阶段id")
    data_source: Optional[StrictStr] = Field(description="数据来源")
    test_time: Optional[str] = Field(description="测试/分析时间")
    test_user: Optional[StrictStr] = Field(description="测试/分析人员")
    car_body: Literal["三厢车", "两厢车", "SUV"] = Field(description="车身形式")
    front_suspension: Literal["麦弗逊", "双叉臂"] = Field(description="前悬形式")
    front_subframe: Literal["全副车架弹性连接", "全副车架刚性连接", "带第三路径半副车架", "半副车架"] = Field(description="前副车架")
    backend_suspension: Literal["五连杆式", "四连杆式", "扭转梁式", "潘哈杆式"] = Field(description="后悬形式")
    backend_subframe: Literal["框式弹性连接", "框式刚性连接"] = Field(description="后副车架")

    @validator("test_time", always=True)
    def check_test_time(cls, test_time, values, config, field):
        if not test_time:
            return ''
        else:
            if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', test_time):
                return test_time
            else:
                raise ValueError('wrong format, must be yyyy-MM-dd HH:mm:ss')


class SingleBaseObj(BaseModel):
    value: float = Field(description='值')
    score: float = Field(description='分值')
            

class ChassisBaseValidate(BaseModel):
    radiation_sound: SingleBaseObj = Field(description='轮胎-胎面辐射声（轮胎选型）')
    peak_frequency: SingleBaseObj = Field(description='轮胎-力传递峰值频率')
    force_transfer: SingleBaseObj = Field(description='轮胎-力传递峰值')
    stability_performance: SingleBaseObj = Field(description='轮胎-操稳性能')
    durability: SingleBaseObj = Field(description='轮胎-耐久性能')
    rim_stiffness_a: SingleBaseObj = Field(description='轮辋刚度-16-17’')
    rim_stiffness_b: SingleBaseObj = Field(description='轮辋刚度-18-19’')
    full_bend_mode: SingleBaseObj = Field(description='前副车架（自由-自由）-全副车架(bend)模态')
    half_bend_mode: SingleBaseObj = Field(description='前副车架（自由-自由）-半副车架(bend)模态')
    torsion_beam: SingleBaseObj = Field(description='后副车架（自由-自由）-类型一：扭转梁(bend)模态')
    multi_link: SingleBaseObj = Field(description='后副车架（自由-自由）-类型二：多连杆(横梁弯曲)模态')
    tire_score: SingleBaseObj = Field(default=0, description='轮胎总分')


class SingleDetailObj(BaseModel):
    molecule: float = Field(description='分子')
    denominator: float = Field(description='分母')
    stiffness_ratio: float = Field(description='刚度比')
    score: float = Field(description='分值')


class ChassisDetailValidate(BaseModel):
    handling_x: SingleDetailObj = Field(description='前下摆臂handling衬套-X向静刚度')
    handling_y: SingleDetailObj = Field(description='前下摆臂handling衬套-Y向静刚度')
    handling_z: SingleDetailObj = Field(description='前下摆臂handling衬套-Z向静刚度')
    handling_stability: SingleDetailObj = Field(description='前下摆臂handling衬套-操稳性能')
    handling_durability: SingleDetailObj = Field(description='前下摆臂handling衬套-耐久性能')
    ride_x: SingleDetailObj = Field(description='前下摆臂ride衬套-X向静刚度')
    ride_y: SingleDetailObj = Field(description='前下摆臂ride衬套-Y向静刚度')
    ride_z: SingleDetailObj = Field(description='前下摆臂ride衬套-Z向静刚度')
    ride_stability: SingleDetailObj = Field(description='前下摆臂ride衬套-操稳性能')
    ride_durability: SingleDetailObj = Field(description='前下摆臂ride衬套-耐久性能')
    front_subframe_x: SingleDetailObj = Field(description='后副车架前衬套-X向静刚度')
    front_subframe_y: SingleDetailObj = Field(description='后副车架前衬套-Y向静刚度')
    front_subframe_z: SingleDetailObj = Field(description='后副车架前衬套-Z向静刚度')
    front_subframe_stability: SingleDetailObj = Field(description='后副车架前衬套-操稳性能')
    front_subframe_durability: SingleDetailObj = Field(description='后副车架前衬套-耐久性能')
    backend_subframe_x: SingleDetailObj = Field(description='后副车架后衬套-X向静刚度')
    backend_subframe_y: SingleDetailObj = Field(description='后副车架后衬套-Y向静刚度')
    backend_subframe_z: SingleDetailObj = Field(description='后副车架后衬套-Z向静刚度')
    backend_subframe_stability: SingleDetailObj = Field(description='后副车架后衬套-操稳性能')
    backend_subframe_durability: SingleDetailObj = Field(description='后副车架后衬套-耐久性能')
    blade_arm_x: SingleDetailObj = Field(description='刀锋臂衬套-X向静刚度')
    blade_arm_y: SingleDetailObj = Field(description='刀锋臂衬套-Y向静刚度')
    blade_arm_z: SingleDetailObj = Field(description='刀锋臂衬套-Z向静刚度')
    blade_arm_stability: SingleDetailObj = Field(description='刀锋臂衬套-操稳性能')
    blade_arm_durability: SingleDetailObj = Field(description='刀锋臂衬套-耐久性能')


class ChassisUpdateValidate(BaseModel):
    chassis_base_info: ChassisBaseValidate
    chassis_detail_info: ChassisDetailValidate


class GetCarTestInfo(BaseModel):
    dev_stage_id: int


class DownloadFileParams(BaseModel):
    fp: str


class ExcelInfo(BaseModel):
    name: str
    url: str


class SaveFreqData(BaseModel):
    save_type: str
    excel_info: List[ExcelInfo]


class GetSelectFreqData(BaseModel):
    select_type: str
    select_car_id: int


class CalculateBaseScore(BaseModel):
    cal_type: str
    num: float


class CalculateDetailScore(BaseModel):
    cal_type: str
    molecule: float
    denominator: float

