from datetime import timedelta
from unittest.mock import Mock

from models.login_model import (
    GetAccessToken,
    GetAuthentication,
    LoginRequest,
    OtpVerification,
    TokenRequest,
)
from services import login_service
from services.login_service import LoginService


def test_get_authentication_adds_otp_and_tokens(monkeypatch):
    service = LoginService()
    result = GetAuthentication(
        User_SK=12,
        UserName="alice",
        Role_SK=3,
        UserType_SK=2,
        Company_SK=9,
        OTPLoginflg=0,
        SendMobileOTP=True,
    )
    service.login_repository = Mock()
    service.login_repository.get_authentication.return_value = result
    create_access_token = Mock(return_value="access-token")
    create_refresh_token = Mock(return_value="refresh-token")
    monkeypatch.setattr(login_service, "create_access_token", create_access_token)
    monkeypatch.setattr(login_service, "create_refresh_token", create_refresh_token)

    response = service.get_authentication(LoginRequest(UserName="alice"))

    assert response.MobileOTP == "0000"
    assert response.Token == "access-token"
    assert response.Refresh_Token == "refresh-token"
    assert response.ExpireOn == str(
        timedelta(minutes=login_service.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    create_access_token.assert_called_once_with(
        {
            "sub": "alice",
            "user_sk": 12,
            "role_sk": 3,
            "user_type_sk": 2,
            "company_sk": 9,
        }
    )
    create_refresh_token.assert_called_once_with(
        {"sub": "alice", "user_sk": 12}
    )


def test_get_authentication_returns_none_without_issuing_tokens(monkeypatch):
    service = LoginService()
    service.login_repository = Mock()
    service.login_repository.get_authentication.return_value = None
    create_access_token = Mock()
    monkeypatch.setattr(login_service, "create_access_token", create_access_token)

    assert service.get_authentication(LoginRequest(UserName="unknown")) is None

    create_access_token.assert_not_called()


def test_otp_verification_issues_tokens_for_verified_user(monkeypatch):
    service = LoginService()
    result = OtpVerification(User_Sk=12, UserName="alice", Role_SK=3, UserType_SK=2)
    service.login_repository = Mock()
    service.login_repository.otp_verification.return_value = result
    create_access_token = Mock(return_value="access-token")
    create_refresh_token = Mock(return_value="refresh-token")
    monkeypatch.setattr(login_service, "create_access_token", create_access_token)
    monkeypatch.setattr(login_service, "create_refresh_token", create_refresh_token)

    response = service.otp_verification(12, "1234")

    assert response is result
    service.login_repository.otp_verification.assert_called_once_with(12, "1234")
    create_access_token.assert_called_once_with(
        {
            "sub": "alice",
            "user_sk": 12,
            "role_sk": 3,
            "user_type_sk": 2,
        }
    )
    create_refresh_token.assert_called_once_with(
        {"sub": "alice", "user_sk": 12}
    )


def test_refresh_token_returns_new_access_token_for_refresh_token(monkeypatch):
    service = LoginService()
    decode_token = Mock(
        return_value={"type": "refresh", "sub": "alice", "user_sk": 12}
    )
    create_access_token = Mock(return_value="new-access-token")
    monkeypatch.setattr(login_service, "decode_token", decode_token)
    monkeypatch.setattr(login_service, "create_access_token", create_access_token)
    request = TokenRequest(Auth_Token="current-access", Rf_Token="refresh-token")

    result = service.refresh_token(request)

    assert result == GetAccessToken(
        NewAccessToken="new-access-token",
        ExpireOn=str(timedelta(minutes=login_service.ACCESS_TOKEN_EXPIRE_MINUTES)),
    )
    decode_token.assert_called_once_with("refresh-token")
    create_access_token.assert_called_once_with(
        {"sub": "alice", "user_sk": 12}
    )


def test_refresh_token_rejects_access_token_type(monkeypatch):
    service = LoginService()
    monkeypatch.setattr(
        login_service,
        "decode_token",
        Mock(return_value={"type": "access", "sub": "alice", "user_sk": 12}),
    )
    create_access_token = Mock()
    monkeypatch.setattr(login_service, "create_access_token", create_access_token)

    result = service.refresh_token(
        TokenRequest(Auth_Token="current-access", Rf_Token="access-token")
    )

    assert result is None
    create_access_token.assert_not_called()
