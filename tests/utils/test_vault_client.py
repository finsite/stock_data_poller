import os
from unittest.mock import patch

import pytest

from app.utils.vault_client import VaultClient


@patch.dict(
    os.environ,
    {
        "VAULT_ADDR": "http://localhost:8200",
        "VAULT_ROLE_ID": "dummy-role-id",
        "VAULT_SECRET_ID": "dummy-secret-id",
        "POLLER_NAME": "test_poller",
        "ENVIRONMENT": "test",
    },
)
@patch("hvac.Client")
def test_vault_client_get(mock_hvac_client):
    mock_instance = mock_hvac_client.return_value
    mock_instance.auth.approle.login.return_value = {"auth": {"client_token": "dummy-token"}}
    mock_instance.secrets.kv.v2.read_secret_version.return_value = {
        "data": {"data": {"EXAMPLE_KEY": "example_value"}}
    }

    client = VaultClient()
    assert client.get("EXAMPLE_KEY") == "example_value"
    assert client.get("MISSING_KEY", "default") == "default"
    assert client.get("MISSING_KEY") is None
