import logging
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    UserUpdateForm,
    CustomPasswordChangeForm,
    PasswordResetRequestForm,
    SetNewPasswordForm
)
from .models import UserProfile, ActivityLog
from contracts.models import Contract

logger = logging.getLogger(__name__)


class LoginView(FormView):
    """
    View para autenticação de usuários
    """
    template_name = 'core/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('core:dashboard')

    @method_decorator(sensitive_post_parameters('password'))
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        # Registrar atividade de login
        ActivityLog.objects.create(
            user=user,
            action_type='login',
            details='Login realizado com sucesso',
            ip_address=self.get_client_ip()
        )
        
        messages.success(self.request, f'Bem-vindo(a), {user.get_full_name() or user.username}!')
        return super().form_valid(form)

    def form_invalid(self, form):
        username = form.data.get('username')
        logger.warning(f'Tentativa de login falha para o usuário: {username}')
        messages.error(self.request, 'Usuário ou senha inválidos. Por favor, tente novamente.')
        return super().form_invalid(form)
    
    def get_client_ip(self):
        """Obtém o endereço IP do cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class LogoutView(RedirectView):
    """
    View para logout de usuários
    """
    url = reverse_lazy('core:login')
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Registrar atividade de logout
            ActivityLog.objects.create(
                user=request.user,
                action_type='logout',
                details='Logout realizado com sucesso',
                ip_address=self.get_client_ip()
            )
            
            logout(request)
            messages.info(request, 'Você saiu do sistema com sucesso.')
        return super().get(request, *args, **kwargs)
    
    def get_client_ip(self):
        """Obtém o endereço IP do cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    View para o dashboard principal do sistema
    """
    template_name = 'core/dashboard.html'
    login_url = '/login/'
    redirect_field_name = 'next'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Estatísticas de contratos
        contracts = Contract.objects.all()
        
        # Contratos por status
        contracts_by_status = Contract.objects.values('status__name').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Contagem de contratos ativos
        active_contracts = contracts.filter(is_active=True).count()
        
        # Contratos vencendo em breve (próximos 30 dias)
        today = timezone.now().date()
        thirty_days_later = today + timedelta(days=30)
        expiring_soon = contracts.filter(
            end_date__range=[today, thirty_days_later],
            is_active=True
        ).count()
        
        # Contratos vencidos
        expired_contracts = contracts.filter(
            end_date__lt=today,
            is_active=True
        ).count()
        
        # Valor total dos contratos ativos
        total_contracts_value = contracts.filter(
            is_active=True
        ).aggregate(total=Sum('value'))['total'] or 0
        
        # Atividades recentes
        recent_activities = ActivityLog.objects.select_related('user').order_by('-timestamp')[:10]
        
        # Próximos vencimentos
        upcoming_contracts = contracts.filter(
            end_date__gte=today,
            is_active=True
        ).order_by('end_date')[:5]
        
        context.update({
            'active_menu': 'dashboard',
            'total_contracts': contracts.count(),
            'active_contracts': active_contracts,
            'expiring_soon_count': expiring_soon,
            'expired_contracts_count': expired_contracts,
            'total_contracts_value': total_contracts_value,
            'contracts_by_status': contracts_by_status,
            'recent_activities': recent_activities,
            'upcoming_contracts': upcoming_contracts,
        })
        
        return context


class UserProfileView(LoginRequiredMixin, UpdateView):
    """
    View para edição do perfil do usuário
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'core/profile.html'
    success_url = reverse_lazy('core:profile')
    
    def get_object(self, queryset=None):
        return self.request.user.profile
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_menu'] = 'profile'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)


class UserPasswordChangeView(LoginRequiredMixin, FormView):
    """
    View para alteração de senha do usuário
    """
    form_class = CustomPasswordChangeForm
    template_name = 'core/password_change.html'
    success_url = reverse_lazy('core:profile')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.save()
        # Atualizar a sessão para não deslogar o usuário
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(self.request, form.user)
        
        messages.success(self.request, 'Sua senha foi alterada com sucesso!')
        return super().form_valid(form)


class UserRegistrationView(FormView):
    """
    View para registro de novos usuários
    """
    template_name = 'core/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('core:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        user = form.save()
        
        # Criar perfil do usuário
        UserProfile.objects.create(
            user=user,
            phone=form.cleaned_data.get('phone', ''),
            is_admin=form.cleaned_data.get('is_admin', False)
        )
        
        # Registrar atividade
        ActivityLog.objects.create(
            user=user,
            action_type='user_register',
            details='Novo usuário registrado',
            ip_address=self.get_client_ip()
        )
        
        messages.success(
            self.request, 
            'Cadastro realizado com sucesso! Faça login para continuar.'
        )
        return super().form_valid(form)
    
    def get_client_ip(self):
        """Obtém o endereço IP do cliente"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class ActivityLogView(LoginRequiredMixin, TemplateView):
    """
    View para exibir o histórico de atividades
    """
    template_name = 'core/activity_log.html'
    paginate_by = 20
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        activities = ActivityLog.objects.select_related('user')
        
        # Filtros
        action_type = self.request.GET.get('action_type')
        if action_type:
            activities = activities.filter(action_type=action_type)
        
        user_id = self.request.GET.get('user')
        if user_id:
            activities = activities.filter(user_id=user_id)
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            try:
                date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
                activities = activities.filter(timestamp__date__gte=date_from)
            except (ValueError, TypeError):
                pass
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            try:
                date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
                activities = activities.filter(timestamp__date__lte=date_to)
            except (ValueError, TypeError):
                pass
        
        # Ordenação
        activities = activities.order_by('-timestamp')
        
        # Paginação
        from django.core.paginator import Paginator
        paginator = Paginator(activities, self.paginate_by)
        page = self.request.GET.get('page')
        
        try:
            activities_page = paginator.page(page)
        except:
            activities_page = paginator.page(1)
        
        context.update({
            'active_menu': 'activity_log',
            'activities': activities_page,
            'action_types': ActivityLog.ACTION_TYPES,
            'selected_action_type': action_type,
            'selected_user': int(user_id) if user_id and user_id.isdigit() else None,
            'date_from': date_from.strftime('%Y-%m-%d') if date_from else '',
            'date_to': date_to.strftime('%Y-%m-%d') if date_to else '',
            'users': User.objects.filter(activity_logs__isnull=False).distinct(),
        })
        
        return context


# Views para tratamento de erros HTTP
def handler400(request, exception, template_name='errors/400.html'):
    """Tratamento para erro 400 - Bad Request"""
    return render(request, template_name, status=400)

def handler403(request, exception, template_name='errors/403.html'):
    """Tratamento para erro 403 - Forbidden"""
    return render(request, template_name, status=403)

def handler404(request, exception, template_name='errors/404.html'):
    """Tratamento para erro 404 - Not Found"""
    return render(request, template_name, status=404)

def handler500(request, template_name='errors/500.html'):
    """Tratamento para erro 500 - Internal Server Error"""
    return render(request, template_name, status=500)
