from repositories.state_repository import StateRepository
from models.state_model import (
    StateModel, 
    StateListModel,
    SaveStateModel,
    UpdateStateModel,
    DeleteStateModel,
    GetCountriesDrpModel,
    GetCountryStateModel
)

class StateService:

    def __init__(self):
        self.state_repository = StateRepository()

    # =========================================================
    # GET STATE LIST
    # =========================================================
    def get_state_list(self):

        result = self.state_repository.get_state_list()

        if result is None:
            return None

        return result

    def get_country_state(self, country_sk):

        result = self.state_repository.get_country_state(country_sk)

        if result is None:
            return None

        return result

    def get_countries_dropdown(self):
        result = self.state_repository.get_countries_dropdown()

        if result is None:
            return None

        return result

    def save_state(self, save_state_model: SaveStateModel):
        result = self.state_repository.save_state(save_state_model)
        return result

    def update_state(self, update_state_model: UpdateStateModel):
        return self.state_repository.update_state(update_state_model)

    def delete_state(self, delete_state_model: DeleteStateModel):
        return self.state_repository.delete_state(delete_state_model)
    