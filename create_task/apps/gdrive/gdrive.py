# -*- coding: utf-8 -*-

import httplib2
import apiclient.discovery
from apiclient import errors
from oauth2client.client import OAuth2Credentials


class GDrive(object):
    EDITOR_ROLE = "editor"
    READER_ROLE = "reader"

    def __init__(self, credentials_json):
        http = httplib2.Http()
        credentials = OAuth2Credentials.from_json(credentials_json)
        credentials.authorize(http)
        self.service = apiclient.discovery.build('drive', 'v2', http=http)

    def update_file(self, title, description, mime_type, file_id):
        file = self.service.files().get(fileId=file_id).execute()

        file['title'] = title
        file['description'] = description
        file['mimeType'] = mime_type

        self.service.files().update(fileId=file_id,
                                    body=file,
                                    newRevision=True).execute()

    def create_file(self, title, description, mime_type):
        body = {
            'title': title,
            'description': description,
            'mimeType': mime_type
        }

        try:
            file = self.service.files().insert(body=body).execute()
            return file
        except errors.HttpError, error:
            print 'Cant create file: %s' % error
            return None

    def get_permissions(self, file_id):
        try:
            permissions = self.service.permissions().list(fileId=file_id).execute()
            return permissions.get('items', [])
        except errors.HttpError, error:
            print 'Cant get permission: %s' % error
        return None

    def create_readers_and_editors(self, file_id, readers, editors):
        for editor in editors:
            self.insert_permission(
                file_id=file_id,
                value=editor.email,
                role=self.EDITOR_ROLE
            )

        for reader in readers:
            self.insert_permission(
                file_id=file_id,
                value=reader.email,
                role=self.READER_ROLE
            )

    def insert_permission(self, file_id, value, role, perm_type="user"):
        new_permission = {
            'value': value,
            'type': perm_type,
            'role': role
        }
        try:
            return self.service.permissions().insert(fileId=file_id, body=new_permission).execute()
        except errors.HttpError, error:
            print 'Cant insert permission: %s' % error
        return None

    def delete_permission(self, file_id, permission_id):
        try:
            self.service.permissions().delete(fileId=file_id, permissionId=permission_id).execute()
        except errors.HttpError, error:
            print 'Cant delete permission: %s' % error

    def rewrite_permissions(self, file_id, readers, editors):
        permissions = self.get_permissions(file_id)

        for x in permissions:
            if x["role"] != "owner":
                self.delete_permission(file_id, x["id"])

        self.create_readers_and_editors(file_id, readers, editors)
        return permissions