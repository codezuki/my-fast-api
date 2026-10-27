from fastapi import APIRouter, Depends

from models.login_model import LoginRequest, TokenRequest
from services.login_service import LoginService


router = APIRouter(
    prefix="/api/Login",
    tags=["Login"]
)


login_service = LoginService()


# =========================================================
# GET AUTHENTICATION
# =========================================================
@router.get("/Auth/GetAuthentication")
def get_authentication(
    login_request: LoginRequest = Depends()
):
    result = login_service.get_authentication(login_request)

    if result is None:
        return {
            "StatusCode": 400,
            "Message": "No User Found!"
        }

    return result


# =========================================================
# OTP VERIFICATION
# =========================================================
@router.get("/Auth/OtpVerification")
def otp_verification(
    User_SK: int,
    OTPValue: str
):
    result = login_service.otp_verification(
        User_SK,
        OTPValue
    )

    if result is None:
        return {
            "StatusCode": 400,
            "Message": "No Record Found!"
        }

    return result


# =========================================================
# GET NEW TOKEN
# =========================================================
@router.post("/Auth/GetNewToken")
def refresh_token(
    request: TokenRequest
):
    result = login_service.refresh_token(request)

    if result is None:
        return {
            "StatusCode": 401,
            "Message": "Invalid refresh token"
        }

    return result