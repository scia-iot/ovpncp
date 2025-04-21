from unittest.mock import MagicMock, patch

from fastapi import HTTPException, Request
from fastapi.testclient import TestClient

from sciaiot.ovpncp.main import app
from sciaiot.ovpncp.middlewares.azure_security import check_role, get_token

client = TestClient(app)

@patch('sciaiot.ovpncp.middlewares.azure_security.TENANT_ID', 'mocked_tenant_id')
@patch('sciaiot.ovpncp.middlewares.azure_security.APP_CLIENT_ID', 'mocked_app_client_id')
@patch('sciaiot.ovpncp.middlewares.azure_security.APP_ROLE', 'mocked_app_role')
@patch('sciaiot.ovpncp.middlewares.azure_security.validate_token', return_value={'sub': 'mocked_sub'})
def test_azure_security_middleware_success(mock_validate_token):
    response = client.get('/')
    assert response.status_code == 404
    
    mock_validate_token.assert_called_once()


@patch('sciaiot.ovpncp.middlewares.azure_security.TENANT_ID', 'mocked_tenant_id')
@patch('sciaiot.ovpncp.middlewares.azure_security.APP_CLIENT_ID', 'mocked_app_client_id')
@patch('sciaiot.ovpncp.middlewares.azure_security.APP_ROLE', 'mocked_app_role')
@patch('sciaiot.ovpncp.middlewares.azure_security.validate_token', side_effect=HTTPException(status_code=401, detail='Mocked Exception'))
def test_azure_security_middleware_failure(mock_validate_token):
    response = client.get('/')
    assert response.status_code == 401
    assert response.json() == {'detail': 'Mocked Exception'}
    
    mock_validate_token.assert_called_once()


def test_get_token_valid():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Bearer some_token"
    token = get_token(request)
    assert token == "some_token"


def test_get_token_no_authorization_header():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = None
    try:
        get_token(request)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Authorization header is expected!"


def test_get_token_invalid_prefix():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "BearerToken some_token"
    try:
        get_token(request)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == 'Authorization header must start with "Bearer"!'


def test_get_token_no_token():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Bearer"
    try:
        get_token(request)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Token not found!"


def test_get_token_multiple_parts():
    request = MagicMock(spec=Request)
    request.headers.get.return_value = "Bearer some_token extra_part"
    try:
        get_token(request)
    except HTTPException as e:
        assert e.status_code == 401
        assert e.detail == "Authorization header must be Bearer token!"


@patch('sciaiot.ovpncp.middlewares.azure_security.APP_ROLE', 'mocked_app_role')
@patch('sciaiot.ovpncp.middlewares.azure_security.jwt.get_unverified_claims', return_value={"roles": ["mocked_app_role"]})
def test_check_role_valid(mock_get_unverified_claims):
    token = "some_token"
    check_role(token)
    mock_get_unverified_claims.assert_called_once_with(token)


@patch('sciaiot.ovpncp.middlewares.azure_security.APP_ROLE', 'mocked_app_role')
@patch('sciaiot.ovpncp.middlewares.azure_security.jwt.get_unverified_claims', return_value={})
def test_check_role_incorrect(mocked_get_unverified_claims):
    token = "some_token"
    try:
        check_role(token)
    except HTTPException as e:
        assert e.status_code == 403
        assert e.detail == 'Application role mocked_app_role is required!'
    
    mocked_get_unverified_claims.assert_called_once_with(token)
