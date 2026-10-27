from fastapi import APIRouter, Depends, HTTPException, Query, status

from models.state_model import (
    DeleteStateModel,
    SaveStateModel,
    UpdateStateModel,
)
from services.state_service import StateService
from utils.auth import get_current_user

router = APIRouter(
    prefix="/api/State",
    tags=["State"]
)

state_service = StateService()

@router.get("/GetStateList")
def get_state_list(current_user=Depends(get_current_user)):
    result = state_service.get_state_list()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No states found")
    return result

@router.get("/GetCountryState")
def get_country_state(
    country_sk: int = Query(gt=0),
    current_user=Depends(get_current_user),
):
    result = state_service.get_country_state(country_sk)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No states found for this country")
    return result

@router.get("/GetCountriesDropdown")
def get_countries_dropdown(current_user=Depends(get_current_user)):
    result = state_service.get_countries_dropdown()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No countries found")
    return result

@router.post("/SaveState")
def save_state(save_state_model: SaveStateModel, current_user=Depends(get_current_user)):
    result = state_service.save_state(save_state_model)
    if result is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="State could not be saved")
    return result

@router.put("/UpdateState")
def update_state(
    update_state_model: UpdateStateModel,
    current_user=Depends(get_current_user),
):
    result = state_service.update_state(update_state_model)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
    return result

@router.delete("/DeleteState")
def delete_state(
    delete_state_model: DeleteStateModel,
    current_user=Depends(get_current_user),
):
    result = state_service.delete_state(delete_state_model)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="State not found")
    return result
