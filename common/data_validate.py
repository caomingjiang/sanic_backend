from pydantic import BaseModel, StrictInt, StrictStr


class LoginValidate(BaseModel):
    account: StrictStr
    password: StrictStr