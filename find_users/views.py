# django's libs
from django.views.generic.edit import FormMixin
from django.contrib.auth.models import User
from django.urls import reverse
# this app's libs
from .forms import FindForm


class FindFormView(FormMixin):
    def __init__(self):
        self.form_class = FindForm
        self.initial = {'find_field': ''}
        self.queryset = None
        self.find_flag: bool = False

    def get(self, request, *args, **kwargs):
        if not self.find_flag:
            self.clear_form()
        if self.find_flag:
            self.find_flag = False

    def post(self, request, *args, **kwargs):
        # setup
        self.user = request.user
        self.find_flag = True
        # working with form
        find_form = FindForm(request.POST)
        if find_form.is_valid():
            self.initial['find_field'] = find_form.cleaned_data['find_field']

    def get_form(self):
        return self.form_class(initial=self.initial)

    def get_context_data(self, **kwargs):
        kwargs['find_form'] = self.get_form()
        kwargs['users_list'] = self._get_users_list()
        kwargs['find_flag'] = True if self.initial['find_field'] else False
        # kwargs['find_flag'] = self.find_flag
        return kwargs

    def get_filtered_queryset(self, queryset):
        filter_by = self.initial['find_field']
        self.queryset = queryset
        queryset = queryset.filter(to_user__username__startswith=filter_by)
        return queryset

    def clear_form(self):
        self.initial['find_field'] = ''

    def _get_users_list(self):
        filter_by = self.initial['find_field']
        if filter_by:
            users_list = User.objects.filter(username__startswith=filter_by)
            users_list = users_list.exclude(id=self.user.id)
            if self.queryset:
                users_list = users_list.exclude(id__in=self._get_own_users_list())
        else:
            users_list = None
        return users_list

    def _get_own_users_list(self):
        users_list_id = []
        for query in self.queryset:
            users_list_id.append(query.to_user.id)
        return users_list_id
