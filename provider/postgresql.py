from typing import Any
import psycopg2
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class PostgresqlProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            conn = psycopg2.connect(
                dbname=credentials["pg_database"],
                user=credentials["pg_user"],
                password=credentials["pg_password"],
                host=credentials["pg_host"],
                port=credentials["pg_port"]
            )
            conn.close()
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"DB connection failed: {e}")
