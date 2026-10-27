import json
from datetime import datetime

from db.db_connection import get_db_connection
from models.login_model import (
    BranchInfo,
    CompanyInfo,
    GetAuthentication,
    OtpVerification,
    BranchHubListRes
)

from utils import DbMapper, DbExecutor



class LoginRepository:

    # =========================================================
    # GET AUTHENTICATION
    # =========================================================
    def get_authentication(self, login_request):

        connection = get_db_connection()
        cursor = None
        branch_cursor = None

        try:

            cursor = DbExecutor(connection).execute(
                "Com_Login_GET",
                {
                    "Mode": "GetAuthentication",
                    "UserName": login_request.UserName,
                    "Password": login_request.Password,
                    "RequestType": login_request.RequestType
                }
            )

            row = cursor.fetchone()

            if row is None:
                return None

            # -----------------------------------------
            # Authentication
            # -----------------------------------------
            result = DbMapper.map_row(
                row,
                GetAuthentication
            )

            # -----------------------------------------
            # Password expiry
            # -----------------------------------------
            result.IsPwdNeedToChange = self.check_password_expiry(
                result.pwd_ExpireOn
            )

            # -----------------------------------------
            # Company
            # -----------------------------------------
            if cursor.nextset():

                company_row = cursor.fetchone()

                if company_row:

                    company = DbMapper.map_row(
                        company_row,
                        CompanyInfo
                    )

                    result.Company_SK = company.Company_SK
                    result.CompanyName = company.CompanyName
                    result.CompanyRegName = company.CompanyRegName
                    result.GSTNO = company.GSTNO
                    result.Website = company.Website
                    result.EmailID = company.EmailID
                    result.PhoneNo = company.PhoneNo
                    result.LogoPath = company.LogoPath
                    result.HeaderLogoPath = company.HeaderLogoPath

            self._drain_result_sets(cursor)

            # -----------------------------------------
            # Default Branch
            # -----------------------------------------
            default_branch = self.get_default_branch(
                result.BranchHubJson
            )

            if default_branch > 0:

                branch_cursor = DbExecutor(connection).execute(
                    "Com_Login_GET",
                    [
                        "GetByBranchHub_Sk",
                        default_branch
                    ]
                )

                branch_row = branch_cursor.fetchone()

                if branch_row:

                    branch = DbMapper.map_row(
                        branch_row,
                        BranchInfo
                    )

                    result.BranchHub_SK = branch.BranchHub_SK
                    result.LimitAmount = branch.LimitAmount
                    result.State_Sk = branch.State_Sk
                    result.IsBooking = branch.IsBooking
                    result.IsDelivery = branch.IsDelivery
                    result.ToBePaid = branch.ToBePaid
                    result.AvailableBalance = branch.AvailableBalance
                    result.IsOwnBranch = branch.IsOwnBranch
                    result.DayRelaxation = branch.DayRelaxation
                    result.IsActiveOrSuspend = branch.IsActiveOrSuspend
                    result.Functional_Type = branch.Functional_Type
                    result.IsApproved = branch.IsApproved
                    result.Latitude = branch.Latitude
                    result.Longitude = branch.Longitude

            return result

        finally:
            try:
                if branch_cursor is not None:
                    branch_cursor.close()
                if cursor is not None:
                    cursor.close()
            finally:
                connection.close()
    # =========================================================
    # OTP VERIFICATION
    # =========================================================
    def otp_verification(
        self,
        user_sk: int,
        otp_value: str
    ):

        connection = get_db_connection()
        cursor = connection.cursor()

        try:

            cursor.execute(
                """
                EXEC Com_Login_GET
                    @Mode = ?,
                    @User_SK = ?,
                    @OTPValue = ?
                """,
                "VerifyOtp",
                user_sk,
                otp_value
            )

            row = cursor.fetchone()

            if row is None:
                return None

            result = OtpVerification()

            result.User_SK = self.get_value(
                row, "User_SK", 0
            )

            result.UserName = self.get_value(
                row, "UserName", None
            )

            result.Role_SK = self.get_value(
                row, "Role_SK", 0
            )

            result.MobileOTP = self.get_value(
                row, "MobileOTP", None
            )

            result.OTPLoginflg = self.get_value(
                row, "OTPLoginflg", 0
            )

            result.Mobileno = self.get_value(
                row, "Mobileno", None
            )

            result.UserType_SK = self.get_value(
                row, "UserType_SK", 0
            )

            result.pwd_ExpireOn = self.get_value(
                row, "pwd_ExpireOn", None
            )

            result.RoleName = self.get_value(
                row, "RoleName", None
            )

            result.Corporate_SK = self.get_value(
                row, "Corporate_SK", 0
            )

            result.EntityType = self.get_value(
                row, "EntityType", 0
            )

            result.District_SK = self.get_value(
                row, "District_SK", 0
            )

            result.BK_UI_Dev_atTop = self.get_value(
                row, "BK_UI_Dev_atTop", None
            )

            branch_json = self.get_value(
                row, "BranchHubJSON", None
            )

            result.BranchHubJson = self.get_branch_hubs(
                branch_json
            )

            return result

        finally:

            cursor.close()
            connection.close()

    # =========================================================
    # HELPER - GET VALUE
    # =========================================================
    @staticmethod
    def get_value(row, column_name, default=None):

        try:
            value = getattr(row, column_name)

            if value is None:
                return default

            return value

        except AttributeError:

            return default

    # =========================================================
    # BRANCH HUB JSON
    # =========================================================
    def get_branch_hubs(self, branch_json):

        if not branch_json:
            return []

        try:

            data = json.loads(branch_json)

            result = []

            for item in data:

                result.append(
                    BranchHubListRes(
                        BH_SK=item.get("BH_SK", 0),
                        BranchHubName=item.get(
                            "BranchHubName"
                        ),
                        IsDefault=item.get(
                            "IsDefault", False
                        )
                    )
                )

            return result

        except Exception:

            return []

    @staticmethod
    def _drain_result_sets(cursor):
        if cursor.description is not None:
            cursor.fetchall()

        while cursor.nextset():
            if cursor.description is not None:
                cursor.fetchall()

    # =========================================================
    # DEFAULT BRANCH
    # =========================================================
    @staticmethod
    def get_default_branch(branch_hubs):

        for branch in branch_hubs:

            if branch.IsDefault:
                return branch.BH_SK

        return 0

    # =========================================================
    # PASSWORD EXPIRY
    # =========================================================
    @staticmethod
    def check_password_expiry(expire_date):

        if not expire_date:
            return False

        try:

            expiry = datetime.strptime(
                str(expire_date),
                "%d-%m-%Y"
            ).date()

            return expiry <= datetime.today().date()

        except ValueError:

            return False

    # =========================================================
    # USER TYPE
    # =========================================================
    @staticmethod
    def get_user_type_description(user_type_sk):

        # TODO:
        # Connect this with UserManagementRepository
        # when that repository is created.

        return None