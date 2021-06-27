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
    

class SingleCarBodyObj(BaseModel):
    value: str = Field(default=None, description='值')
    score: float = Field(description='分值')

    
class SaveCarBodyData(BaseModel):
    biw_gtmf: SingleCarBodyObj = Field(description='白车身 -- 全局扭转模态频率')
    biw_gbmf: SingleCarBodyObj = Field(description='白车身 -- 全局弯曲模态频率')
    cring_vc: SingleCarBodyObj = Field(description='C ring -- Visual Check')
    fwall_lps: SingleCarBodyObj = Field(description='前围 -- 大板刚度')
    no1_beam_vc: SingleCarBodyObj = Field(description='一号梁 -- Visual Check')
    floor_lps: SingleCarBodyObj = Field(description='地板 -- 大板刚度')
    fawsp_vc: SingleCarBodyObj = Field(description='地板无支撑板面积 -- Visual Check')
    swcf_lps: SingleCarBodyObj = Field(description='备胎舱地板 -- 大板刚度')
    dorpfswc_vc: SingleCarBodyObj = Field(description='备胎舱加强板设计 -- Visual Check')
    ceiling_lps: SingleCarBodyObj = Field(description='顶棚 -- 大板刚度')
    ceiling_st_vc: SingleCarBodyObj = Field(description='顶棚结构 -- Visual Check')
    lwhip_lps: SingleCarBodyObj = Field(description='左轮罩内板 -- 大板刚度')
    rsarp_vc: SingleCarBodyObj = Field(description='后减震器加强板 -- Visual Check')
    rwhip_lps: SingleCarBodyObj = Field(description='右轮罩内板 -- 大板刚度')
    rsop_lps: SingleCarBodyObj = Field(description='后侧围外板 -- 大板刚度')
    coat_rack_lps: SingleCarBodyObj = Field(description='衣帽架 -- 大板刚度')
    flume_lps: SingleCarBodyObj = Field(description='落水槽 -- 大板刚度')
    dotsotwt_vc: SingleCarBodyObj = Field(description='落水槽支架设计 -- Visual Check')


class CalculateCarBodyScore(BaseModel):
    cal_type: str
    value: str


class ImageInfo(BaseModel):
    name: str
    url: str


class SaveDesignLibrary(BaseModel):
    data_type: str
    col: str
    images: List[ImageInfo] = Field(default=[])


class AnalysisDesignLibraryZip(BaseModel):
    name: str
    url: str


class SaveWeightSettingsData(BaseModel):
    save_type: str
    excel_info: List[ExcelInfo]


class SaveAticPkgConfsData(BaseModel):
    name: str
    url: str
    

class SingleAticPkgData(BaseModel):
    active_conf: str = Field(description="当前选中选项")
    

class SaveAcousticPackageData(BaseModel):
    fwsa_aoc: SingleAticPkgData = Field(description="前围吸隔声_落水槽盖板空调新风口吸音棉Absorber on cowl")
    fwsa_fa: SingleAticPkgData = Field(description="前围吸隔声_前翼子板吸音棉Fender absorber")
    fwsa_gv: SingleAticPkgData = Field(description="前围吸隔声_前围内隔音垫(汽油机车型Gasoline Vehicle)")
    fwsa_hev: SingleAticPkgData = Field(description="前围吸隔声_前围内隔音垫(混合动力车型HEV)")
    fwsa_ev: SingleAticPkgData = Field(description="前围吸隔声_前围内隔音垫(纯电动车型EV)")
    fsaai_fsmt: SingleAticPkgData = Field(description="地板吸隔声_地板钣金厚度")
    fsaai_lbautf: SingleAticPkgData = Field(description="地板吸隔声_地板下大电池敷设面积")
    fsaai_fc: SingleAticPkgData = Field(description="地板吸隔声_主地毯隔音垫Floor Carpet")
    fsaai_mcip_fc: SingleAticPkgData = Field(description="地板吸隔声_主地毯隔音垫Floor Carpet(电池铺在地板下的车型)")
    fsaai_tbtbp: SingleAticPkgData = Field(description="地板吸隔声_地板下电池包与地板间的密封(电池铺在地板下的车型)")
    fsaai_rsls: SingleAticPkgData = Field(description="地板吸隔声_后座椅下部隔音垫")
    fsaai_bdprp: SingleAticPkgData = Field(description="地板吸隔声_车身阻尼垫、加强垫（前围、地板、顶盖、侧围、行李厢）")
    fsaai_ufpsac: SingleAticPkgData = Field(description="地板吸隔声_地板下护板（导流板）及吸音棉")
    swcf_hsac: SingleAticPkgData = Field(description="备胎舱地板吸隔声_三厢车衣帽架吸音棉")
    swcf_ttia: SingleAticPkgData = Field(description="备胎舱地板吸隔声_举升门内饰板吸音棉Tailgate trim inside absorber")
    swcf_tc: SingleAticPkgData = Field(description="备胎舱地板吸隔声_行李箱地毯")
    swcf_sipis: SingleAticPkgData = Field(description="备胎舱地板吸隔声_备胎舱内隔音垫")
    saaiowh_isms: SingleAticPkgData = Field(description="轮罩吸隔声_后轮罩内钣金隔音垫")
    saaiowh_wh: SingleAticPkgData = Field(description="轮罩吸隔声_轮罩")
    saaiowh_bceb: SingleAticPkgData = Field(description="轮罩吸隔声_车身空腔膨胀块Baffle")
    saaiorsw_saca: SingleAticPkgData = Field(description="后侧围吸隔声_后轮罩上方吸声棉(后侧围空腔隔音棉)")
    saaiorsw_itpor: SingleAticPkgData = Field(description="后侧围吸隔声_后侧围内饰板及其吸音棉")
    saaiosd_iposd: SingleAticPkgData = Field(description="侧门吸隔声_侧门内饰板及其吸音棉")
    saaiosd_dpd: SingleAticPkgData = Field(description="侧门吸隔声_车门板阻尼")
    saaiosd_dwm: SingleAticPkgData = Field(description="侧门吸隔声_车门防水膜")


class SingleDataConfsFiles(BaseModel):
    name: str
    url: str


class SaveSingleDataConfsData(BaseModel):
    save_type: str
    files: List[SingleDataConfsFiles] = Field(default=[])
