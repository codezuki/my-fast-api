from repositories.login_repository import LoginRepository
from models.login_model import (
    LoginRequest,
    TokenRequest,
    GetAccessToken
)
from utils.jwt_handler import (
    create_access_token,
    create_refresh_token,
    decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from datetime import timedelta


class LoginService:

    def __init__(self):
        self.login_repository = LoginRepository()

    # =========================================================
    # GET AUTHENTICATION
    # =========================================================
    def get_authentication(
        self,
        login_request: LoginRequest
    ):

        result = self.login_repository.get_authentication(
            login_request
        )

        if result is None:
            return None

        # -----------------------------------------
        # OTP Logic
        # -----------------------------------------
        if (
            result.OTPLoginflg == 0
            and result.SendMobileOTP is True
        ):

            # SMS service will be added later

            result.MobileOTP = "0000"

        # -----------------------------------------
        # Logo Logic
        # -----------------------------------------
        if (
            result.HeaderLogoPath is not None
            and result.LogoPath is not None
        ):

            # Image URL service will be added later
            pass

        # -----------------------------------------
        # JWT Logic
        # -----------------------------------------
        token_payload = {
            "sub": result.UserName,
            "user_sk": result.User_SK,
            "role_sk": result.Role_SK,
            "user_type_sk": result.UserType_SK,
            "company_sk": result.Company_SK,
        }

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(
            {"sub": result.UserName, "user_sk": result.User_SK}
        )

        result.Token = access_token
        result.ExpireOn = str(
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        result.Refresh_Token = refresh_token

        return result

    # =========================================================
    # OTP VERIFICATION
    # =========================================================
    def otp_verification(
        self,
        user_sk: int,
        otp_value: str
    ):

        result = self.login_repository.otp_verification(
            user_sk,
            otp_value
        )

        if result is None:
            return None

        # Issue tokens after successful OTP verification
        token_payload = {
            "sub": result.UserName,
            "user_sk": result.User_Sk,
            "role_sk": result.Role_SK,
            "user_type_sk": result.UserType_SK,
        }

        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(
            {"sub": result.UserName, "user_sk": result.User_Sk}
        )

        # Attach to result if fields exist
        if hasattr(result, "Token"):
            result.Token = access_token
        if hasattr(result, "Refresh_Token"):
            result.Refresh_Token = refresh_token

        return result

    # =========================================================
    # REFRESH TOKEN
    # =========================================================
    def refresh_token(
        self,
        request: TokenRequest
    ):

        if not request.Rf_Token:
            return None

        if not request.Auth_Token:
            return None

        try:
            payload = decode_token(request.Rf_Token)
        except Exception:
            return None

        if payload.get("type") != "refresh":
            return None

        user_sk = payload.get("user_sk")
        user_name = payload.get("sub")

        new_access = create_access_token(
            {"sub": user_name, "user_sk": user_sk}
        )

        return GetAccessToken(
            NewAccessToken=new_access,
            ExpireOn=str(timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
        )
