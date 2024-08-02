import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


def upload_to_drive(temp_csv_path, creds_json, folder_id, file_metadata, **kwargs):
    # Get credentials from the provided JSON string
    creds_dict = json.loads(creds_json)
    creds = service_account.Credentials.from_service_account_info(creds_dict)

    drive_service = build("drive", "v3", credentials=creds)

    # Check if file exists
    query = f"name = '{file_metadata['name']}' and '{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        file_id = files[0]["id"]
        # Update existing file
        media = MediaFileUpload(temp_csv_path, mimetype="text/csv")
        updated_file = (
            drive_service.files()
            .update(fileId=file_id, body={}, media_body=media, fields="id")
            .execute()
        )
        print(f"File updated in Google Drive with ID: {updated_file.get('id')}")
    else:
        # Create new file if it does not exist
        file_metadata["parents"] = [folder_id]
        media = MediaFileUpload(temp_csv_path, mimetype="text/csv")
        new_file = (
            drive_service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        print(f"File uploaded to Google Drive with ID: {new_file.get('id')}")

    # Optionally, remove the temporary file
    os.remove(temp_csv_path)
