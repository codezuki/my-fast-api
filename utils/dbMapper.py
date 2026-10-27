class DbMapper:

    @staticmethod
    def map_rows(cursor, model):
        columns = [column[0] for column in cursor.description]
        return [
            DbMapper._map_row_values(row, columns, model)
            for row in cursor.fetchall()
        ]

    @staticmethod
    def map_row(row, model):
        columns = [column[0] for column in row.cursor_description]
        return DbMapper._map_row_values(row, columns, model)

    @staticmethod
    def _map_row_values(row, columns, model):
        row_data = {
            column.lower(): row[index]
            for index, column in enumerate(columns)
        }
        model_data = {
            field_name: row_data[field_name.lower()]
            for field_name in model.model_fields
            if field_name.lower() in row_data
        }
        return model.model_validate(model_data)