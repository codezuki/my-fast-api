from fastapi import APIRouter
from db.db_connection import get_db_connection
router =  APIRouter()


@router.get("/myApi")
def home():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute("SELECT GETDATE() as date,1 as [key],DB_NAME() AS database_name")

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return {
        "message": "Welcome to my first API",
        "database_time": str(result.date),
        "key": result.key,
        "database_name": result.database_name
    }
