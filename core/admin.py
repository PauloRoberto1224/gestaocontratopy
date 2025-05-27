from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse

from .models import User, UserProfile, ActivityLog, SystemSettings


class UserCreationFormExtended(UserCreationForm):
    """Formulário de criação de usuário personalizado"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class UserChangeFormExtended(UserChangeForm):
    """Formulário de edição de usuário personalizado"""
    class Meta:
        model = User
        fields = '__all__'


class UserProfileInline(admin.StackedInline):
    """Inline para o perfil do usuário"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = _('perfil')
    fk_name = 'user'
    fields = (
        'phone', 'birth_date', 'gender', 'avatar_preview',
        'address', 'address_number', 'address_complement',
        'neighborhood', 'city', 'state', 'zip_code', 'country',
        'language', 'timezone', 'receive_newsletter', 'email_notifications'
    )
    readonly_fields = ('avatar_preview',)
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.avatar.url
            )
        return _("Nenhuma imagem de perfil")
    
    avatar_preview.short_description = _('Pré-visualização')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Configuração do painel de administração para o modelo User"""
    form = UserChangeFormExtended
    add_form = UserCreationFormExtended
    
    list_display = (
        'email', 'first_name', 'last_name', 'is_staff',
        'is_active', 'date_joined', 'last_login'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações Pessoais'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Permissões'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            )
        }),
        (_('Datas Importantes'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    
    inlines = [UserProfileInline]
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Configuração do painel de administração para o modelo UserProfile"""
    list_display = (
        'user', 'get_email', 'phone', 'city', 'state',
        'created_at', 'updated_at'
    )
    list_filter = ('gender', 'state', 'city', 'created_at')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'phone', 'city', 'state'
    )
    readonly_fields = ('created_at', 'updated_at', 'avatar_preview')
    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Informações Pessoais'), {
            'fields': (
                'phone', 'birth_date', 'gender',
                'avatar', 'avatar_preview'
            )
        }),
        (_('Endereço'), {
            'fields': (
                'address', 'address_number', 'address_complement',
                'neighborhood', 'city', 'state', 'zip_code', 'country'
            )
        }),
        (_('Preferências'), {
            'fields': (
                'language', 'timezone',
                'receive_newsletter', 'email_notifications'
            )
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = _('Email')
    get_email.admin_order_field = 'user__email'
    
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 200px;" />',
                obj.avatar.url
            )
        return _("Nenhuma imagem de perfil")
    
    avatar_preview.short_description = _('Pré-visualização')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Configuração do painel de administração para o modelo ActivityLog"""
    list_display = ('action_type_display', 'user_display', 'ip_address', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'ip_address', 'details'
    )
    readonly_fields = ('timestamp', 'user_agent_display')
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        (None, {
            'fields': ('action_type', 'user_display', 'timestamp')
        }),
        (_('Detalhes'), {
            'fields': ('details',)
        }),
        (_('Informações Técnicas'), {
            'fields': ('ip_address', 'user_agent_display'),
            'classes': ('collapse',)
        }),
    )
    
    def action_type_display(self, obj):
        return obj.get_action_type_display()
    action_type_display.short_description = _('Tipo de Ação')
    action_type_display.admin_order_field = 'action_type'
    
    def user_display(self, obj):
        if obj.user:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:core_user_change', args=[obj.user.id]),
                str(obj.user)
            )
        return _('Sistema')
    user_display.short_description = _('Usuário')
    user_display.admin_order_field = 'user__email'
    
    def user_agent_display(self, obj):
        return obj.user_agent or _('Não disponível')
    user_agent_display.short_description = _('User Agent')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    """Configuração do painel de administração para o modelo SystemSettings"""
    list_display = ('name', 'key', 'setting_type', 'is_public', 'updated_at')
    list_filter = ('setting_type', 'is_public')
    search_fields = ('key', 'name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_public',)
    
    fieldsets = (
        (None, {
            'fields': ('key', 'name', 'description', 'is_public')
        }),
        (_('Valor'), {
            'fields': ('setting_type', 'value')
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Garante que a chave seja salva em minúsculas e sem espaços
        obj.key = obj.key.lower().strip()
        super().save_model(request, obj, form, change)


# Configurações do painel de administração
admin.site.site_header = _('Painel de Administração')
admin.site.site_title = _('Sistema de Gestão de Contratos')
admin.site.index_title = _('Bem-vindo ao Painel de Administração')
