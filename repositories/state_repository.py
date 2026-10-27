import json
from datetime import datetime

from db.db_connection import get_db_connection
from models.state_model import (
    StateModel,
    StateListModel,
    SaveStateModel,
    UpdateStateModel,
    DeleteStateModel,
    GetCountriesDrpModel,
    GetCountryStateModel
)

from utils.dbMapper import DbMapper
from utils.spExecutor import DbExecutor
from utils.cache import cache


class StateRepository:
    procedureName=""
    action=""
    # =========================================================
    # GET STATE LIST
    # =========================================================
    def get_state_list(self):
        cache_key = "state:list"

        def load():
            connection = get_db_connection()
            cursor = None
            try:
                cursor = DbExecutor(connection).execute(
                    "Com_State_GET", {"Mode": "GETALL"}
                )
                result = DbMapper.map_rows(cursor, StateModel)
                if not result:
                    return None
                return StateListModel(StateList=result)
            finally:
                try:
                    if cursor is not None:
                        cursor.close()
                finally:
                    connection.close()

        return cache.get_or_set(cache_key, load)

    def get_country_state(self, country_sk):
        cache_key = f"state:country:{country_sk}"

        def load():
            connection = get_db_connection()
            cursor = None
            try:
                cursor = DbExecutor(connection).execute(
                    "Com_State_GET",
                    {"Mode": "GETBYCOUNTRY", "Country_SK": country_sk},
                )
                result = DbMapper.map_rows(cursor, StateModel)
                if not result:
                    return None
                return GetCountryStateModel(
                    Country_SK=country_sk,
                    StateList=result,
                )
            finally:
                try:
                    if cursor is not None:
                        cursor.close()
                finally:
                    connection.close()

        return cache.get_or_set(cache_key, load)

    def get_countries_dropdown(self):
        cache_key = "state:countries_dropdown"

        def load():
            connection = get_db_connection()
            cursor = None
            try:
                cursor = DbExecutor(connection).execute(
                    "Com_CommonMaster_GET", {"Mode": "GetCountry"}
                )
                return DbMapper.map_rows(cursor, GetCountriesDrpModel)
            finally:
                try:
                    if cursor is not None:
                        cursor.close()
                finally:
                    connection.close()

        return cache.get_or_set(cache_key, load)

    def save_state(self, save_state_model: SaveStateModel):
        connection = get_db_connection()
        cursor = None
        try:
            params = {
                "Mode": "INSERT",
                "StateName": save_state_model.StateName,
                "StateCode": save_state_model.StateCode,
                "Country_SK": save_state_model.Country_SK,
                "IsActive": save_state_model.IsActive,
                "User_SK": save_state_model.User_SK,
            }
            cursor = DbExecutor(connection).execute("Com_State_Trans", params)
            row = cursor.fetchone()
            if row is None:
                return None
            result = DbMapper.map_row(row, StateModel)
            connection.commit()
            cache.delete("state:list")
            cache.delete_prefix("state:country:")
            return result
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def update_state(self, update_state_model: UpdateStateModel):
        return self._write_state(
            "UPDATE",
            {
                "State_SK": update_state_model.State_SK,
                "StateName": update_state_model.StateName,
                "StateCode": update_state_model.StateCode,
                "Country_SK": update_state_model.Country_SK,
                "IsActive": update_state_model.IsActive,
                "User_SK": update_state_model.User_SK,
            },
        )

    def delete_state(self, delete_state_model: DeleteStateModel):
        return self._write_state(
            "DELETE",
            {
                "State_SK": delete_state_model.State_SK,
                "User_SK": delete_state_model.User_SK,
            },
        )

    @staticmethod
    def _write_state(mode: str, params: dict):
        connection = get_db_connection()
        cursor = None
        try:
            cursor = DbExecutor(connection).execute(
                "Com_State_Trans", {"Mode": mode, **params}
            )
            row = cursor.fetchone()
            if row is None:
                return None
            result = DbMapper.map_row(row, StateModel)
            connection.commit()
            cache.delete("state:list")
            cache.delete_prefix("state:country:")
            return result
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()
