"""
Mixin classes for common view functionality across the project.
"""

from django.contrib.auth.mixins import (
    LoginRequiredMixin as BaseLoginRequiredMixin,
    PermissionRequiredMixin as BasePermissionRequiredMixin,
    UserPassesTestMixin as BaseUserPassesTestMixin,
)
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _


class LoginRequiredMixin(BaseLoginRequiredMixin):
    """
    Mixin to ensure user is logged in.
    Redirects to login page if not authenticated.
    """
    login_url = reverse_lazy('core:login')
    redirect_field_name = 'next'


class PermissionRequiredMixin(BasePermissionRequiredMixin):
    """
    Mixin to verify that the current user has specified permissions.
    """
    login_url = reverse_lazy('core:login')
    permission_denied_message = _("You don't have permission to access this page.")

    def handle_no_permission(self):
        messages.error(self.request, self.get_permission_denied_message())
        return super().handle_no_permission()


class StaffRequiredMixin(LoginRequiredMixin, BaseUserPassesTestMixin):
    """
    Mixin to ensure user is staff member.
    """
    permission_denied_message = _("Only staff members can access this page.")

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('core:dashboard')


class SuperuserRequiredMixin(LoginRequiredMixin, BaseUserPassesTestMixin):
    """
    Mixin to ensure user is superuser.
    """
    permission_denied_message = _("Only superusers can access this page.")

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return redirect('core:dashboard')


class AjaxResponseMixin:
    """
    Mixin to handle AJAX form submissions.
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'error',
                'errors': form.errors,
            }, status=400)
        return response

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'redirect': self.get_success_url(),
            })
        return response


class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        return JsonResponse(self.get_data(context), **response_kwargs)

    def get_data(self, context):
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.render_to_json_response(context, **response_kwargs)
        return super().render_to_response(context, **response_kwargs)


class SuccessMessageMixin:
    """
    Add a success message on successful form submission.
    """
    success_message = ""

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data

    def form_valid(self, form):
        response = super().form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response


class FormInvalidMessageMixin:
    """
    Add an error message on invalid form submission.
    """
    form_invalid_message = _("Please correct the errors below.")

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, self.form_invalid_message)
        return response


class ObjectOwnerMixin:
    """
    Mixin to verify object ownership before allowing access.
    """
    owner_field = 'user'
    permission_denied_message = _("You don't have permission to access this object.")

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not self.is_owner(obj):
            messages.error(self.request, self.permission_denied_message)
            raise PermissionDenied
        return obj

    def is_owner(self, obj):
        owner = getattr(obj, self.owner_field, None)
        if owner and hasattr(owner, 'pk'):
            return owner.pk == self.request.user.pk
        return False


class PaginationMixin:
    """
    Mixin to add pagination to list views.
    """
    paginate_by = 20
    page_kwarg = 'page'
    paginate_orphans = 2
    allow_empty = True

    def get_paginate_by(self, queryset):
        return self.request.GET.get('per_page', self.paginate_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_kwarg'] = self.page_kwarg
        return context


class FilterMixin:
    """
    Mixin to add filtering to list views.
    """
    filter_class = None
    filterset_kwargs = {}

    def get_filter_kwargs(self):
        return {
            'data': self.request.GET or None,
            **self.filterset_kwargs,
        }

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.filter_class:
            self.filterset = self.filter_class(
                **self.get_filter_kwargs(),
                queryset=queryset
            )
            return self.filterset.qs.distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'filterset'):
            context['filter'] = self.filterset
        return context
