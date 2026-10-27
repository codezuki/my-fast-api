import logging


logger = logging.getLogger(__name__)


class DbExecutor:

    def __init__(self, connection):
        self.connection = connection

    def execute(self, procedure, params=None):

        cursor = self.connection.cursor()

        params = params or {}

        if isinstance(params, dict):

            assignments = ", ".join(
                f"@{key} = ?" for key in params.keys()
            )

            sql = f"EXEC {procedure} {assignments}"

            values = list(params.values())

        else:

            placeholders = ", ".join(
                "?" for _ in params
            )

            sql = f"EXEC {procedure}"

            if placeholders:
                sql += f" {placeholders}"

            values = params

        logger.info("Executing SQL: %s", sql)

        cursor.execute(
            sql,
            *values
        )

        return cursor