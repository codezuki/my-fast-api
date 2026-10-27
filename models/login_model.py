import json
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    UserName: Optional[str] = None
    Password: Optional[str] = None
    RequestType: int = 0


class TokenRequest(BaseModel):
    Auth_Token: Optional[str] = None
    Rf_Token: Optional[str] = None


class BranchHubList(BaseModel):
    BH_SK: int = 0
    IsDefault: bool = False


class BranchHubListRes(BaseModel):
    BH_SK: int = 0
    BranchHubName: Optional[str] = None
    IsDefault: bool = False

class CompanyInfo(BaseModel):
    Company_SK: int = 0
    CompanyName: Optional[str] = None
    CompanyRegName: Optional[str] = None
    GSTNO: Optional[str] = None
    Website: Optional[str] = None
    EmailID: Optional[str] = None
    PhoneNo: Optional[str] = None
    LogoPath: Optional[str] = None
    HeaderLogoPath: Optional[str] = None

class BranchInfo(BaseModel):
    BranchHub_SK: int = 0
    LimitAmount: float = 0
    State_Sk: int = 0

    IsBooking: bool = False
    IsDelivery: bool = False

    ToBePaid: float = 0
    AvailableBalance: float = 0

    IsOwnBranch: bool = False
    DayRelaxation: bool = False

    IsActiveOrSuspend: int = 0
    Functional_Type: int = 0
    IsApproved: int = 0

    Latitude: float = 0
    Longitude: float = 0

class GetAuthentication(BaseModel):

    # User
    User_SK: int = 0
    UserName: Optional[str] = None

    UserType_SK: int = 0
    UserTypeDesc: Optional[str] = None

    Role_SK: int = 0
    RoleName: Optional[str] = None

    EntityType: int = 0
    Employee_SK: int = 0
    Corporate_SK: int = 0
    District_SK: int = 0

    # Mobile / OTP
    Mobileno: Optional[str] = None
    MobileOTP: Optional[str] = None
    OTPLoginflg: int = 0
    SendMobileOTP: bool = False

    # Password
    pwd_ExpireOn: Optional[str] = None
    IsPwdNeedToChange: bool = False

    # Branch
    BranchHub_SK: int = 0
    BranchHubJson: list[BranchHubListRes] = Field(
        default_factory=list
    )

    LimitAmount: float = 0
    State_Sk: int = 0

    IsBooking: bool = False
    IsDelivery: bool = False

    ToBePaid: float = 0
    AvailableBalance: float = 0

    IsOwnBranch: bool = False
    DayRelaxation: bool = False

    IsActiveOrSuspend: int = 0
    Functional_Type: int = 0
    IsApproved: int = 0

    Latitude: float = 0
    Longitude: float = 0

    # Company
    Company_SK: int = 0
    CompanyName: Optional[str] = None
    CompanyRegName: Optional[str] = None
    GSTNO: Optional[str] = None
    Website: Optional[str] = None
    EmailID: Optional[str] = None
    PhoneNo: Optional[str] = None
    LogoPath: Optional[str] = None
    HeaderLogoPath: Optional[str] = None

    # UI
    BK_UI_Dev_atTop: Optional[bool] = None

    # Token
    Token: Optional[str] = None
    ExpireOn: Optional[str] = None
    Refresh_Token: Optional[str] = None   

    @field_validator("MobileOTP", mode="before")
    @classmethod
    def normalize_mobile_otp(cls, value: Any) -> Optional[str]:
        return None if value is None else str(value)

    @field_validator("BranchHubJson", mode="before")
    @classmethod
    def parse_branch_hubs(cls, value: Any) -> Any:
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return json.loads(value)
        return value

class GetAccessToken(BaseModel):
    NewAccessToken: Optional[str] = None
    ExpireOn: Optional[str] = None


class OtpVerification(BaseModel):
    User_Sk: int = 0
    UserName: Optional[str] = None

    Role_SK: int = 0

    MobileOTP: Optional[str] = None
    OTPLoginflg: int = 0
    Mobileno: Optional[str] = None

    UserType_SK: int = 0

    pwd_ExpireOn: Optional[str] = None

    RoleName: Optional[str] = None

    Corporate_SK: int = 0
    EntityType: int = 0

    BranchHubJson: list[BranchHubListRes] = Field(
        default_factory=list
    )

    BK_UI_Dev_atTop: Optional[bool] = None

    District_SK: int = 0