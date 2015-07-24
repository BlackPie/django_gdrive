# -*- coding: utf-8 -*-

from oauth2client import client
from django.shortcuts import redirect
from django.views.generic.base import View
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout
from django.views.generic.edit import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, ListView, UpdateView

from forms import DocumentForm, UserCreateForm
from create_task.apps.gdrive.models import Document


class OAuthMixin(object):
    def get(self, request, *args, **kwargs):
        if "credentials" not in request.session:
            flow = client.flow_from_clientsecrets(
                        'client_secrets.json',
                        scope='https://www.googleapis.com/auth/drive',
                        redirect_uri="http://localhost:8000/oauth")
            if 'code' not in request.REQUEST:
                auth_uri = flow.step1_get_authorize_url()
                return redirect(auth_uri)
            else:
                auth_code = request.REQUEST.get('code')
                credentials = flow.step2_exchange(auth_code)
                request.session['credentials'] = credentials.to_json()
                return redirect(request.get_full_path())
        else:
            return super(OAuthMixin, self).get(self, request)


class OAuthView(View):
    def get(self, request):
        flow = client.flow_from_clientsecrets(
                    'client_secrets.json',
                    scope='https://www.googleapis.com/auth/drive.metadata.readonly',
                    redirect_uri="http://localhost:8000/oauth")

        if 'code' not in request.REQUEST:
            auth_uri = flow.step1_get_authorize_url()
            return redirect(auth_uri)
        else:
            auth_code = request.REQUEST.get('code')
            credentials = flow.step2_exchange(auth_code)
            request.session['credentials'] = credentials.to_json()
            return redirect(reverse('document_list'))


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view, login_url="login/")


class AuthMixin(OAuthMixin, LoginRequiredMixin):
    pass


class FormProcessingOverrideMixin(object):
    """
    Миксин для выноса обработки формы из view
    """
    def post(self, request, *args, **kwargs):
        form = self.get_form()

        document_object = None
        if self.model:
            document_object = self.get_object()

        if form.is_valid(request, document_object):
            return self.form_valid()
        else:
            return self.form_invalid(form)

    def form_valid(self):
        return HttpResponseRedirect(self.get_success_url())


class DocumentUpdateView(AuthMixin, FormProcessingOverrideMixin, UpdateView):
    model = Document
    form_class = DocumentForm
    template_name = 'gdrive/create_document.html'
    succes_url = '/'

    def get_success_url(self):
        return self.succes_url


class DocumentCreateView(AuthMixin, FormProcessingOverrideMixin, CreateView):
    form_class = DocumentForm
    template_name = 'gdrive/create_document.html'
    succes_url = '/'

    def get_success_url(self):
        return self.succes_url


class LogoutView(AuthMixin, View):
    def get(self, request):
        logout(request)
        return HttpResponseRedirect("/")


class LoginFormView(FormView):
    form_class = AuthenticationForm
    template_name = "gdrive/register.html"
    success_url = "/"

    def form_valid(self, form):
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginFormView, self).form_valid(form)


class RegisterFormView(FormView):
    form_class = UserCreateForm
    success_url = "/login/"
    template_name = "gdrive/register.html"

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)


class DocumentListView(AuthMixin, ListView):
    model = Document
    queryset = Document.objects.all().order_by("updated")

    def get_context_data(self, **kwargs):
        context = super(DocumentListView, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            for document in context["object_list"]:
                document.access_status(self.request.user)

        return context
