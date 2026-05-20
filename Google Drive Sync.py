import os
import hashlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_NAME = 'DESTINASI'

def get_local_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def authenticate_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=False)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(service, folder_name, parent_id=None):
    safe_folder_name = folder_name.replace("'", "\\'")
    query = f"mimeType='application/vnd.google-apps.folder' and name='{safe_folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    else:
        query += " and 'root' in parents"
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if not items:
        print(f"[BARU] Membuat folder di Drive: {folder_name}")
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            folder_metadata['parents'] = [parent_id]
        folder = service.files().create(body=folder_metadata, fields='id').execute()
        return folder.get('id')
    return items[0].get('id')

def get_file_in_drive(service, file_name, parent_id):
    safe_file_name = file_name.replace("'", "\\'")
    query = f"name='{safe_file_name}' and '{parent_id}' in parents and trashed=false and mimeType!='application/vnd.google-apps.folder'"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name, md5Checksum)').execute()
    items = results.get('files', [])
    if items:
        return items[0]
    return None

def sync_folder(service, local_path, drive_parent_id):
    for item in os.listdir(local_path):
        item_path = os.path.join(local_path, item)
        
        if os.path.isfile(item_path):
            local_md5 = get_local_md5(item_path)
            drive_file = get_file_in_drive(service, item, drive_parent_id)
            
            if drive_file:
                drive_md5 = drive_file.get('md5Checksum')
                if local_md5 == drive_md5:
                    print(f"--> [LEWAT] File sudah sama: {item}")
                    continue
                else:
                    print(f"--> [UPDATE] Memperbarui file yang berubah: {item}")
                    media = MediaFileUpload(item_path, resumable=True)
                    service.files().update(fileId=drive_file.get('id'), media_body=media).execute()
            else:
                print(f"--> [UNGGAH] Mengunggah file baru: {item}")
                file_metadata = {'name': item, 'parents': [drive_parent_id]}
                media = MediaFileUpload(item_path, resumable=True)
                service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                
        elif os.path.isdir(item_path):
            print(f"\n--> [MASUK] Memproses sub-folder lokal: {item}")
            new_drive_folder_id = get_or_create_folder(service, item, drive_parent_id)
            sync_folder(service, item_path, new_drive_folder_id)

def main():
    print("--> Memulai Proses Sinkronisasi Backup Google Drive")
    service = authenticate_drive()
    
    root_folder_id = get_or_create_folder(service, DRIVE_FOLDER_NAME)
    
    list_folder_lokal = [
        r'E:\local', 
        r'D:\local'
    ]
    
    for folder_path in list_folder_lokal:
        if os.path.exists(folder_path):
            nama_folder_asli = os.path.basename(folder_path.strip(r'\/'))
            print(f"\n>>> Memproses direktori utama: {folder_path} -> Menjadi folder Drive: {nama_folder_asli}")
            
            target_drive_id = get_or_create_folder(service, nama_folder_asli, root_folder_id)
            
            sync_folder(service, folder_path, target_drive_id)
        else:
            print(f"\n[PERINGATAN] Folder tidak ditemukan di komputer: {folder_path}")
        
    print("--> Semua proses pencadangan selesai dengan aman!")

if __name__ == '__main__':
    main()
