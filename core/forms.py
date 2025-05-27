from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

from .models import User, UserProfile, SystemSettings


class UserRegistrationForm(UserCreationForm):
    """Formulário de registro de novo usuário"""
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('seu@email.com')
        })
    )
    first_name = forms.CharField(
        label=_('Nome'),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu nome')
        })
    )
    last_name = forms.CharField(
        label=_('Sobrenome'),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu sobrenome')
        })
    )
    password1 = forms.CharField(
        label=_('Senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Crie uma senha forte')
        }),
        help_text=_(
            'Sua senha não pode ser muito parecida com suas outras informações pessoais.<br>'
            'Sua senha precisa conter pelo menos 8 caracteres.<br>'
            'Sua senha não pode ser uma senha comumente usada.<br>'
            'Sua senha não pode ser inteiramente numérica.'
        )
    )
    password2 = forms.CharField(
        label=_('Confirmação de senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a mesma senha novamente')
        })
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Este email já está em uso. Por favor, use outro email.'))
        return email


class UserLoginForm(AuthenticationForm):
    """Formulário de login de usuário"""
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('seu@email.com'),
            'autofocus': True
        })
    )
    password = forms.CharField(
        label=_('Senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Sua senha')
        })
    )

    error_messages = {
        'invalid_login': _(
            "Por favor, insira um email e senha corretos. "
            "Note que ambos os campos diferenciam maiúsculas e minúsculas."
        ),
        'inactive': _("Esta conta está inativa."),
    }


class UserProfileForm(forms.ModelForm):
    """Formulário para edição do perfil do usuário"""
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("O número de telefone deve estar no formato: '+999999999'. Até 15 dígitos.")
    )
    
    phone = forms.CharField(
        label=_('Telefone'),
        validators=[phone_regex],
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('+55 11 99999-9999')
        })
    )
    
    birth_date = forms.DateField(
        label=_('Data de Nascimento'),
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'class': 'form-control'
            }
        ),
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']
    )
    
    avatar = forms.ImageField(
        label=_('Foto de Perfil'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'birth_date', 'gender', 'avatar',
            'address', 'address_number', 'address_complement',
            'neighborhood', 'city', 'state', 'zip_code', 'country',
            'language', 'timezone', 'receive_newsletter', 'email_notifications'
        ]
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'address_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_complement': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.Select(attrs={'class': 'form-select'}),
            'zip_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '00000-000',
                'data-mask': '00000-000'
            }),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.Select(attrs={'class': 'form-select'}),
            'receive_newsletter': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserUpdateForm(forms.ModelForm):
    """Formulário para atualização dos dados básicos do usuário"""
    email = forms.EmailField(
        label=_('Email'),
        disabled=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True
        })
    )
    
    first_name = forms.CharField(
        label=_('Nome'),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu nome')
        })
    )
    
    last_name = forms.CharField(
        label=_('Sobrenome'),
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Seu sobrenome')
        })
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']


class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulário personalizado para alteração de senha"""
    old_password = forms.CharField(
        label=_('Senha atual'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Sua senha atual')
        })
    )
    new_password1 = forms.CharField(
        label=_('Nova senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a nova senha')
        }),
        help_text=_(
            'Sua senha não pode ser muito parecida com suas outras informações pessoais.<br>'
            'Sua senha precisa conter pelo menos 8 caracteres.<br>'
            'Sua senha não pode ser uma senha comumente usada.<br>'
            'Sua senha não pode ser inteiramente numérica.'
        )
    )
    new_password2 = forms.CharField(
        label=_('Confirmação da nova senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a nova senha novamente')
        })
    )


class SystemSettingsForm(forms.ModelForm):
    """Formulário para configurações do sistema"""
    class Meta:
        model = SystemSettings
        fields = ['key', 'name', 'description', 'value', 'setting_type', 'is_public']
        widgets = {
            'key': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'value': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'setting_type': forms.Select(attrs={'class': 'form-select'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_key(self):
        key = self.cleaned_data.get('key')
        if key:
            key = key.lower().strip()
            if not re.match(r'^[a-z0-9_]+$', key):
                raise ValidationError(_('A chave deve conter apenas letras minúsculas, números e underscores.'))
        return key


class PasswordResetRequestForm(forms.Form):
    """Formulário para solicitação de redefinição de senha"""
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('seu@email.com'),
            'autocomplete': 'email'
        })
    )


class SetNewPasswordForm(forms.Form):
    """Formulário para definição de uma nova senha"""
    new_password1 = forms.CharField(
        label=_('Nova senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a nova senha')
        }),
        help_text=_(
            'Sua senha não pode ser muito parecida com suas outras informações pessoais.<br>'
            'Sua senha precisa conter pelo menos 8 caracteres.<br>'
            'Sua senha não pode ser uma senha comumente usada.<br>'
            'Sua senha não pode ser inteiramente numérica.'
        )
    )
    new_password2 = forms.CharField(
        label=_('Confirmação da nova senha'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Digite a nova senha novamente')
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', _('As senhas não coincidem.'))
        
        return cleaned_data
