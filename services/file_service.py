from fastapi import UploadFile, HTTPException

from utils.json_parser import JsonParser
from utils.csv_parser import CsvParser


class FileService:

    async def extract_data(self, file: UploadFile):

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="File is required"
            )

        extension = file.filename.split(".")[-1].lower()

        if extension == "json":

            parser = JsonParser()

        elif extension == "csv":

            parser = CsvParser()

        else:

            raise HTTPException(
                status_code=400,
                detail="Only JSON and CSV files are supported"
            )

        try:

            data = await parser.parse(file)

            return {
                "success": True,
                "file_name": file.filename,
                "file_type": extension.upper(),
                "record_count": len(data),
                "data": data
            }

        except Exception as ex:

            raise HTTPException(
                status_code=400,
                detail=f"Unable to process file: {str(ex)}"
            )