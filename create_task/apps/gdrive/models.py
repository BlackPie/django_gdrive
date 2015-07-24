# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User


GD_DOC_TYPES = [
    ("table", "application/vnd.google-apps.spreadsheet",),
    ("doc", "application/vnd.google-apps.document",),
    ("form", "application/vnd.google-apps.form",)
]


class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    url = models.URLField()

    gd_id = models.CharField(max_length=200, null=True, blank=True)
    doc_type = models.CharField(choices=GD_DOC_TYPES, max_length=255, blank=True)

    owner = models.ForeignKey(User, related_name="owner")
    editor_list = models.ManyToManyField(User, related_name="editors", blank=True)
    reader_list = models.ManyToManyField(User, related_name="readers", blank=True)

    def access_status(self, user):
        self.status = ''
        self.updatable = False

        if user == self.owner:
            self.status = "owner"
            self.updatable = True
        elif user in self.editor_list.all():
            self.status = "editor"
            self.updatable = True
        elif user in self.reader_list.all():
            self.status = "reader"

    def update(self, newdata):
        for key, value in newdata.iteritems():
            setattr(self, key, value)
