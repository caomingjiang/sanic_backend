from pydantic import BaseModel, StrictInt, StrictStr, Field, validator, constr
from typing import Optional
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
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', test_time):
                return test_time
            else:
                raise ValueError('wrong format, must be yyyy-MM-dd HH:mm:ss')


class GetCarTestInfo(BaseModel):
    dev_stage_id: int
