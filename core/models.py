import os
import uuid
from datetime import timedelta
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


def user_directory_path(instance, filename):
    """
    Função para gerar o caminho do diretório de upload de arquivos do usuário
    Formato: user_<id>/<filename>
    """
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"user_{instance.user.id}/{filename}"


class User(AbstractUser):
    """
    Modelo de usuário personalizado que estende o modelo de usuário padrão do Django
    """
    email = models.EmailField(_('endereço de email'), unique=True)
    is_verified = models.BooleanField(_('verificado'), default=False)
    
    # Campos adicionais podem ser adicionados aqui
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def get_absolute_url(self):
        return reverse('core:user_detail', kwargs={'pk': self.pk})


class UserProfile(models.Model):
    """
    Perfil estendido para o modelo de usuário
    """
    GENDER_CHOICES = (
        ('M', _('Masculino')),
        ('F', _('Feminino')),
        ('O', _('Outro')),
        ('N', _('Prefiro não informar')),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('usuário')
    )
    
    # Informações pessoais
    phone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    birth_date = models.DateField(_('data de nascimento'), blank=True, null=True)
    gender = models.CharField(
        _('gênero'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    
    # Localização
    address = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    address_number = models.CharField(_('número'), max_length=20, blank=True, null=True)
    address_complement = models.CharField(
        _('complemento'),
        max_length=100,
        blank=True,
        null=True
    )
    neighborhood = models.CharField(_('bairro'), max_length=100, blank=True, null=True)
    city = models.CharField(_('cidade'), max_length=100, blank=True, null=True)
    state = models.CharField(_('estado'), max_length=2, blank=True, null=True)
    zip_code = models.CharField(_('CEP'), max_length=10, blank=True, null=True)
    country = models.CharField(_('país'), max_length=100, default='Brasil')
    
    # Preferências
    language = models.CharField(
        _('idioma'),
        max_length=10,
        choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE
    )
    timezone = models.CharField(
        _('fuso horário'),
        max_length=50,
        default=settings.TIME_ZONE
    )
    
    # Avatar
    avatar = models.ImageField(
        _('foto de perfil'),
        upload_to=user_directory_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif'],
                message=_('Apenas arquivos de imagem são permitidos (JPG, JPEG, PNG, GIF)')
            )
        ]
    )
    
    # Configurações de notificação
    receive_newsletter = models.BooleanField(
        _('receber newsletter'),
        default=True,
        help_text=_('Deseja receber nossas newsletters e atualizações por email?')
    )
    email_notifications = models.BooleanField(
        _('notificações por email'),
        default=True,
        help_text=_('Deseja receber notificações por email?')
    )
    
    # Metadados
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('perfil de usuário')
        verbose_name_plural = _('perfis de usuários')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    def get_full_address(self):
        """Retorna o endereço completo formatado"""
        parts = []
        if self.address:
            parts.append(self.address)
            if self.address_number:
                parts.append(self.address_number)
            if self.address_complement:
                parts.append(self.address_complement)
        
        if self.neighborhood:
            parts.append(self.neighborhood)
        
        city_parts = []
        if self.city:
            city_parts.append(self.city)
        if self.state:
            city_parts.append(self.state)
        
        if city_parts:
            parts.append(", ".join(city_parts))
        
        if self.zip_code:
            parts.append(f"CEP: {self.zip_code}")
        
        if self.country and self.country != 'Brasil':
            parts.append(self.country)
        
        return " - ".join(parts) if parts else _("Endereço não informado")


class ActivityLog(models.Model):
    """
    Registro de atividades dos usuários no sistema
    """
    # Tipos de ações
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    PROFILE_UPDATE = 'profile_update'
    USER_CREATE = 'user_create'
    USER_UPDATE = 'user_update'
    USER_DELETE = 'user_delete'
    CONTRACT_CREATE = 'contract_create'
    CONTRACT_UPDATE = 'contract_update'
    CONTRACT_DELETE = 'contract_delete'
    CONTRACT_RENEW = 'contract_renew'
    CONTRACT_EXPIRE = 'contract_expire'
    DOCUMENT_UPLOAD = 'document_upload'
    DOCUMENT_DELETE = 'document_delete'
    NOTIFICATION_SENT = 'notification_sent'
    REPORT_GENERATED = 'report_generated'
    SYSTEM_EVENT = 'system_event'
    
    ACTION_TYPES = (
        (LOGIN, _('Login')),
        (LOGOUT, _('Logout')),
        (PASSWORD_CHANGE, _('Alteração de senha')),
        (PROFILE_UPDATE, _('Atualização de perfil')),
        (USER_CREATE, _('Criação de usuário')),
        (USER_UPDATE, _('Atualização de usuário')),
        (USER_DELETE, _('Exclusão de usuário')),
        (CONTRACT_CREATE, _('Criação de contrato')),
        (CONTRACT_UPDATE, _('Atualização de contrato')),
        (CONTRACT_DELETE, _('Exclusão de contrato')),
        (CONTRACT_RENEW, _('Renovação de contrato')),
        (CONTRACT_EXPIRE, _('Expiração de contrato')),
        (DOCUMENT_UPLOAD, _('Upload de documento')),
        (DOCUMENT_DELETE, _('Exclusão de documento')),
        (NOTIFICATION_SENT, _('Notificação enviada')),
        (REPORT_GENERATED, _('Relatório gerado')),
        (SYSTEM_EVENT, _('Evento do sistema')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs',
        verbose_name=_('usuário')
    )
    
    action_type = models.CharField(
        _('tipo de ação'),
        max_length=50,
        choices=ACTION_TYPES,
        db_index=True
    )
    
    details = models.TextField(
        _('detalhes'),
        blank=True,
        null=True
    )
    
    ip_address = models.GenericIPAddressField(
        _('endereço IP'),
        protocol='both',
        unpack_ipv4=True,
        blank=True,
        null=True
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        null=True,
        help_text=_('Informações do navegador do usuário')
    )
    
    timestamp = models.DateTimeField(
        _('data e hora'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        verbose_name = _('registro de atividade')
        verbose_name_plural = _('registros de atividades')
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.user} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action_type, details=None, request=None):
        """
        Método auxiliar para registrar uma ação no log de atividades
        """
        ip_address = None
        user_agent = None
        
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return cls.objects.create(
            user=user,
            action_type=action_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )


class SystemSettings(models.Model):
    """
    Configurações gerais do sistema
    """
    SETTING_TYPES = (
        ('text', _('Texto')),
        ('number', _('Número')),
        ('boolean', _('Verdadeiro/Falso')),
        ('json', _('JSON')),
        ('date', _('Data')),
        ('datetime', _('Data e Hora')),
        ('email', _('Email')),
        ('url', _('URL')),
        ('file', _('Arquivo')),
        ('image', _('Imagem')),
    )
    
    key = models.SlugField(
        _('chave'),
        max_length=100,
        unique=True,
        help_text=_('Nome único para identificar a configuração')
    )
    
    name = models.CharField(
        _('nome'),
        max_length=100,
        help_text=_('Nome amigável para a configuração')
    )
    
    value = models.TextField(
        _('valor'),
        blank=True,
        null=True,
        help_text=_('Valor da configuração')
    )
    
    setting_type = models.CharField(
        _('tipo'),
        max_length=20,
        choices=SETTING_TYPES,
        default='text',
        help_text=_('Tipo de dado da configuração')
    )
    
    description = models.TextField(
        _('descrição'),
        blank=True,
        null=True,
        help_text=_('Descrição detalhada da configuração')
    )
    
    is_public = models.BooleanField(
        _('público'),
        default=True,
        help_text=_('Se falso, apenas administradores podem visualizar/editar')
    )
    
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    
    class Meta:
        verbose_name = _('configuração do sistema')
        verbose_name_plural = _('configurações do sistema')
        ordering = ['key']
    
    def __str__(self):
        return f"{self.name} ({self.key})"
    
    def get_value(self):
        """Retorna o valor no tipo apropriado"""
        if not self.value:
            return None
            
        if self.setting_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.setting_type == 'number':
            try:
                if '.' in self.value:
                    return float(self.value)
                return int(self.value)
            except (ValueError, TypeError):
                return self.value
        elif self.setting_type == 'json':
            import json
            try:
                return json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                return self.value
        elif self.setting_type == 'date':
            from django.utils.dateparse import parse_date
            return parse_date(self.value)
        elif self.setting_type == 'datetime':
            from django.utils.dateparse import parse_datetime
            return parse_datetime(self.value)
        else:
            return self.value
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Obtém uma configuração pelo nome"""
        try:
            setting = cls.objects.get(key=key)
            return setting.get_value()
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, **kwargs):
        """Define ou atualiza uma configuração"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults=kwargs
        )
        
        if not created:
            for attr, val in kwargs.items():
                setattr(setting, attr, val)
        
        setting.value = str(value)
        setting.save()
        return setting


# Sinais
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria um perfil automaticamente quando um novo usuário é criado"""
    if created and not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil sempre que o usuário for salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
