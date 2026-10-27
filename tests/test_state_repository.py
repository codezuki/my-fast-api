from unittest.mock import Mock

from models.state_model import SaveStateModel, StateListModel, StateModel
from repositories import state_repository
from repositories.state_repository import StateRepository


def test_get_state_list_maps_rows_and_closes_database_resources(monkeypatch):
    connection = Mock()
    cursor = Mock()
    state = StateModel(State_SK=1, StateName="California", Country_SK=1)
    executor = Mock()
    executor.execute.return_value = cursor
    monkeypatch.setattr(state_repository, "get_db_connection", lambda: connection)
    monkeypatch.setattr(state_repository, "DbExecutor", lambda _: executor)
    monkeypatch.setattr(state_repository.DbMapper, "map_rows", lambda *_: [state])
    monkeypatch.setattr(
        state_repository.cache,
        "get_or_set",
        lambda _key, factory: factory(),
    )

    result = StateRepository().get_state_list()

    assert result == StateListModel(StateList=[state])
    executor.execute.assert_called_once_with(
        "Com_State_GET",
        {"Mode": "GETALL"},
    )
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_get_state_list_returns_none_when_no_rows(monkeypatch):
    connection = Mock()
    cursor = Mock()
    executor = Mock()
    executor.execute.return_value = cursor
    monkeypatch.setattr(state_repository, "get_db_connection", lambda: connection)
    monkeypatch.setattr(state_repository, "DbExecutor", lambda _: executor)
    monkeypatch.setattr(state_repository.DbMapper, "map_rows", lambda *_: [])
    monkeypatch.setattr(
        state_repository.cache,
        "get_or_set",
        lambda _key, factory: factory(),
    )

    assert StateRepository().get_state_list() is None

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_save_state_commits_and_invalidates_state_caches(monkeypatch):
    connection = Mock()
    cursor = Mock()
    saved_state = StateModel(State_SK=1, StateName="California", Country_SK=1)
    cursor.fetchone.return_value = object()
    executor = Mock()
    executor.execute.return_value = cursor
    monkeypatch.setattr(state_repository, "get_db_connection", lambda: connection)
    monkeypatch.setattr(state_repository, "DbExecutor", lambda _: executor)
    monkeypatch.setattr(state_repository.DbMapper, "map_row", lambda *_: saved_state)
    delete = Mock()
    delete_prefix = Mock()
    monkeypatch.setattr(state_repository.cache, "delete", delete)
    monkeypatch.setattr(state_repository.cache, "delete_prefix", delete_prefix)
    request = SaveStateModel(
        StateName="California",
        StateCode="CA",
        Country_SK=1,
        IsActive=True,
        User_SK=7,
    )

    result = StateRepository().save_state(request)

    assert result == saved_state
    executor.execute.assert_called_once_with(
        "Com_State_Trans",
        {
            "Mode": "INSERT",
            "StateName": "California",
            "StateCode": "CA",
            "Country_SK": 1,
            "IsActive": True,
            "User_SK": 7,
        },
    )
    connection.commit.assert_called_once()
    delete.assert_called_once_with("state:list")
    delete_prefix.assert_called_once_with("state:country:")
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
