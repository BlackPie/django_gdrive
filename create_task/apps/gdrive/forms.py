# -*- coding: utf-8 -*-

from django import forms
from models import Document

from gdrive import GDrive
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


DOCUMENT_USER_FIELDS = [
    "reader_list",
    "editor_list"
]


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class DocumentForm(forms.ModelForm):
    class Meta(object):
        model = Document
        exclude = ["created", "updated", "owner", "gd_id", "url"]

    def is_valid(self, request, document_object):
        # import ipdb; pdb.set_trace()
        if self.is_bound and not self.errors:
            # если форма из UpdateView
            if document_object:
                if self.changed_data:
                    document_object.update(self.cleaned_data)
                    document_object.save()
                    gdrive = GDrive(request.session["credentials"])

                    gdrive.update_file(
                        title=document_object.title,
                        description=document_object.title,
                        mime_type=document_object.doc_type,
                        file_id=document_object.gd_id
                    )

                    if set(DOCUMENT_USER_FIELDS) & set(self.changed_data):
                        gdrive.rewrite_permissions(
                            file_id=document_object.gd_id,
                            readers=document_object.reader_list.all(),
                            editors=document_object.editor_list.all()
                        )
                return True
            # если форма из CreateView
            else:
                instance = self.save(commit=False)
                instance.owner = request.user
                instance.save()
                self.save_m2m()

                gdrive = GDrive(request.session["credentials"])

                file = gdrive.create_file(
                    title=instance.title,
                    description=instance.description,
                    mime_type=instance.doc_type,
                )

                instance.gd_id = file["id"]
                instance.url = file["alternateLink"]

                if instance.reader_list or instance.editor_list:
                    gdrive.create_readers_and_editors(
                        file_id=file["id"],
                        readers=instance.reader_list.all(),
                        editors=instance.editor_list.all()
                    )
                instance.save()
            return True
        else:
            return False