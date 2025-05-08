import datetime
import json
import logging
import os
from urllib.parse import quote_plus

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, generate_blob_sas
from fastapi import Request
from fastapi.concurrency import iterate_in_threadpool
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
CONTAINER_NAME = 'ovpncp'

if STORAGE_CONNECTION_STRING:
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    parts = dict(x.split('=', 1) for x in STORAGE_CONNECTION_STRING.split(';') if x)
    account_name = parts.get('AccountName', '')
    account_key = parts.get('AccountKey', '')

async def azure_storage_middleware(request: Request, call_next):
    if STORAGE_CONNECTION_STRING: 
        url_path = request.url.path
        if url_path.endswith('/package-cert'):
            response = await handle_upload(request, call_next)
            return response
        elif url_path.endswith('download-cert'):
            response = await handle_download(request, call_next)
            return response

    response = await call_next(request)
    return response

async def handle_upload(request: Request, call_next):
    response = await call_next(request)
    response_body = [chunk async for chunk in response.body_iterator]
    response.body_iterator = iterate_in_threadpool(iter(response_body))
    
    client_name = request.path_params['client_name']
    archive = json.loads(response_body[0].decode())
    file_path = archive.get('file_path')
    blob_client = container_client.get_blob_client(f'{client_name}.zip')
    
    try:
        with open(file_path, 'rb') as data:
            blob_client.upload_blob(data, overwrite=True)
            logger.info(f'Cert uploaded to Azure Blob Storage: {blob_client.url}')
        response = JSONResponse(content={'file_path': blob_client.url}, status_code=200)
    except Exception as e:
        logger.error(f'Error uploading cert to Azure Blob Storage: {e}')
        response = JSONResponse(content={'detail': 'Error uploading cert to Azure Blob Storage'}, status_code=500)
            
    return response

async def handle_download(request: Request, call_next):
    response = await call_next(request)
    client_name = request.path_params['client_name']
    blob_name = f'{client_name}.zip'
    
    try: 
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=CONTAINER_NAME,
            blob_name=blob_name,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
        )

        
        blob_url = f'https://{account_name}.blob.core.windows.net/{CONTAINER_NAME}/{quote_plus(blob_name)}'
        sas_url = f'{blob_url}?{sas_token}'
        logger.info(f'Generated SAS URL for blob: {sas_url}')
        response = JSONResponse(content={'url': sas_url}, status_code=200)
    except Exception as e:
        logger.error(f'Error generating SAS URL for blob: {e}')
        response = JSONResponse(content={'detail': 'Error generating SAS URL for blob'}, status_code=500)
    
    return response
