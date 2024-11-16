from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
import redis
import os
import random

SCOPES = ["https://www.googleapis.com/auth/drive"]
tabs = {}

def upload_report(fn):
  
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'keys.json', SCOPES)
    try:
        
        service = build("drive", "v3", credentials=creds)

        file_metadata = {"name": fn.split("/")[-1], "parents": ["16yG-r0NOTsKZHL5JXhqoXTzFuyDG68Aq"]}
        media = MediaFileUpload(
            fn, mimetype="text/csv", resumable=True
        )
        
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        # print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

def download_reports():
  
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'keys.json', SCOPES)
    try:

        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        results = (
            service.files()
            .list(q="'16yG-r0NOTsKZHL5JXhqoXTzFuyDG68Aq' in parents", pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        
        for item in items:
            request = service.files().get_media(fileId=item['id'])
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            parts = item['name'].split("_")
            tabs[item['name'][-2:]] = f'{parts[1]} [{parts[2]}]'
            with open(f"reports/{item['name']}", "wb") as f:
                f.write(file.getbuffer())
            file.seek(0)
            r.set(item['name'][-2:], file.getbuffer())
            
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def delete_report(fn):

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'keys.json', SCOPES)
    try:

        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        results = (
            service.files()
            .list(q=f"'16yG-r0NOTsKZHL5JXhqoXTzFuyDG68Aq' in parents and name = '{fn}'", pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        
        for item in items:
            response = service.files().delete(fileId=item['id']).execute()
            
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def list_reports():

    creds = ServiceAccountCredentials.from_json_keyfile_name(
        'keys.json', SCOPES)
    try:

        service = build("drive", "v3", credentials=creds)

        # Call the Drive v3 API
        results = (
            service.files()
            .list(q=f"'16yG-r0NOTsKZHL5JXhqoXTzFuyDG68Aq' in parents", pageSize=10, fields="nextPageToken, files(id, name)")
            .execute()
        )
        items = results.get("files", [])
        
        items = sorted([item["name"] for item in items], reverse=True)
        return items
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")

if __name__ == '__main__':
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    download_reports()
    r.hset("tabs", mapping=tabs)
    r.set('peepo', random.choice(os.listdir('./assets/icons/')))

    



  