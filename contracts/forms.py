from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.conf import settings
from django.db.models import Q
from .models import (
    Contract, ContractType, ContractStatus, ContractParty,
    ContractReminder, ContractAttachment, ContractHistory
)


class ContractFilterForm(forms.Form):
    """Formulário para filtragem de contratos"""
    STATUS_CHOICES = [
        ('', '---------'),
        ('active', 'Ativos'),
        ('expired', 'Expirados'),
        ('expiring_soon', 'Próximos de vencer'),
    ]
    
    search = forms.CharField(
        label=_('Pesquisar'),
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Número, título ou descrição'),
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    contract_type = forms.ModelChoiceField(
        label=_('Tipo de Contrato'),
        queryset=ContractType.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        label=_('Data de Início'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            },
            format='%Y-%m-%d'
        )
    )
    end_date = forms.DateField(
        label=_('Data de Término'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control'
            },
            format='%Y-%m-%d'
        )
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contract_type'].empty_label = _('Todos os tipos')
    
    def filter_queryset(self, queryset):
        data = self.cleaned_data
        
        if data.get('search'):
            search = data['search']
            queryset = queryset.filter(
                Q(contract_number__icontains=search) |
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )
        
        if data.get('status') == 'active':
            from django.utils import timezone
            today = timezone.now().date()
            queryset = queryset.filter(
                end_date__gte=today,
                is_active=True
            )
        elif data.get('status') == 'expired':
            from django.utils import timezone
            today = timezone.now().date()
            queryset = queryset.filter(
                end_date__lt=today,
                is_active=True
            )
        elif data.get('status') == 'expiring_soon':
            from django.utils import timezone
            from datetime import timedelta
            today = timezone.now().date()
            next_30_days = today + timedelta(days=30)
            queryset = queryset.filter(
                end_date__range=[today, next_30_days],
                is_active=True
            )
        
        if data.get('contract_type'):
            queryset = queryset.filter(contract_type=data['contract_type'])
        
        if data.get('start_date'):
            queryset = queryset.filter(start_date__gte=data['start_date'])
        
        if data.get('end_date'):
            queryset = queryset.filter(end_date__lte=data['end_date'])
        
        return queryset


class ContractForm(forms.ModelForm):
    """Formulário para criação e edição de contratos"""
    class Meta:
        model = Contract
        fields = [
            'contract_number', 'company', 'company_cnpj', 'fiscal_name', 'fiscal_registration',
            'alternate_fiscal_name', 'alternate_fiscal_registration',
            'contract_term', 'start_date', 'end_date', 'value', 'currency',
            'contract_document', 'fiscal_portaria', 'additive_term', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(
                attrs={'class': 'form-control dateinput'},
                format='%d/%m/%Y'
            ),
            'end_date': forms.DateInput(
                attrs={'class': 'form-control dateinput'},
                format='%d/%m/%Y'
            ),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'contract_term': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.HiddenInput(),
        }
        help_texts = {
            'fiscal_registration': 'Digite apenas números',
            'alternate_fiscal_registration': 'Digite apenas números',
            'additive_term': 'Obrigatório apenas para termos aditivos',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classes CSS aos campos
        for field in self.fields:
            if field not in ['contract_term', 'currency', 'notes', 'contract_number']:
                if 'class' not in self.fields[field].widget.attrs:
                    self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Configura os campos de matrícula e CNPJ
        self.fields['fiscal_registration'].widget.attrs.update({
            'pattern': '\d{7}',
            'title': 'A matrícula deve conter exatamente 7 dígitos',
            'oninput': 'formatFiscalRegistration($(this))',
            'maxlength': '7'
        })
        
        self.fields['alternate_fiscal_registration'].widget.attrs.update({
            'pattern': '\d{7}',
            'title': 'A matrícula deve conter exatamente 7 dígitos',
            'oninput': 'formatFiscalRegistration($(this))',
            'maxlength': '7'
        })
        
        # Configura o campo CNPJ
        self.fields['company_cnpj'].widget.attrs.update({
            'oninput': 'formatCNPJ($(this))',
            'placeholder': '00.000.000/0000-00',
            'maxlength': '18'
        })
        
        # Define o valor padrão da moeda como BRL e esconde o campo
        self.fields['currency'].initial = 'BRL'
        self.fields['currency'].widget.attrs['value'] = 'BRL'
        
        # Configura o campo de número do contrato como somente leitura
        self.fields['contract_number'].widget.attrs['readonly'] = True
        self.fields['contract_number'].widget.attrs['class'] = 'form-control-plaintext'
        self.fields['contract_number'].help_text = 'Número gerado automaticamente no formato CTR-YYYY-NNN'
    
    def clean_company_cnpj(self):
        cnpj = self.cleaned_data.get('company_cnpj', '').replace('.', '').replace('/', '').replace('-', '')
        if cnpj and (not cnpj.isdigit() or len(cnpj) != 14):
            raise forms.ValidationError('CNPJ inválido. O CNPJ deve conter 14 dígitos.')
        # Formata o CNPJ para o formato 00.000.000/0000-00
        if cnpj:
            cnpj = f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
        return cnpj
    
    def clean_fiscal_registration(self):
        fiscal_registration = self.cleaned_data.get('fiscal_registration', '')
        fiscal_registration = ''.join(filter(str.isdigit, str(fiscal_registration)))
        if fiscal_registration and (not fiscal_registration.isdigit() or len(fiscal_registration) != 7):
            raise forms.ValidationError('A matrícula deve conter exatamente 7 dígitos.')
        return fiscal_registration
    
    def clean_alternate_fiscal_registration(self):
        alt_registration = self.cleaned_data.get('alternate_fiscal_registration', '')
        alt_registration = ''.join(filter(str.isdigit, str(alt_registration)))
        if alt_registration and (not alt_registration.isdigit() or len(alt_registration) != 7):
            raise forms.ValidationError('A matrícula deve conter exatamente 7 dígitos.')
        return alt_registration
    
    def clean(self):
        cleaned_data = super().clean()
        contract_term = cleaned_data.get('contract_term')
        additive_term = cleaned_data.get('additive_term')
        
        # Valida se o termo aditivo foi fornecido para termos aditivos
        if contract_term != 'initial' and not additive_term:
            self.add_error('additive_term', 'É obrigatório anexar o termo aditivo para esta opção.')
        
        return cleaned_data
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise ValidationError({
                'end_date': _('A data de término não pode ser anterior à data de início.')
            })
        return cleaned_data


class ContractTypeForm(forms.ModelForm):
    """Formulário para tipos de contrato"""
    class Meta:
        model = ContractType
        fields = ['name', 'description', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class ContractStatusForm(forms.ModelForm):
    """Formulário para status de contrato"""
    class Meta:
        model = ContractStatus
        fields = ['name', 'description', 'is_active', 'color', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }


class ContractPartyForm(forms.ModelForm):
    """Formulário para partes de contrato"""
    class Meta:
        model = ContractParty
        fields = ['user', 'role', 'is_primary', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class ContractReminderForm(forms.ModelForm):
    """Formulário para lembretes de contrato"""
    class Meta:
        model = ContractReminder
        fields = ['title', 'description', 'due_date', 'assigned_to', 'is_completed']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['due_date'].input_formats = ['%Y-%m-%dT%H:%M']


class ContractAttachmentForm(forms.ModelForm):
    """Formulário para anexos de contrato"""
    class Meta:
        model = ContractAttachment
        fields = ['file', 'name', 'description', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.contract = kwargs.pop('contract', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.contract:
            instance.contract = self.contract
        if self.user:
            instance.uploaded_by = self.user
        if commit:
            instance.save()
        return instance


class ContractHistoryForm(forms.ModelForm):
    """Formulário para histórico de alterações de contrato"""
    class Meta:
        model = ContractHistory
        fields = ['change_description', 'changed_fields']
        widgets = {
            'change_description': forms.Textarea(attrs={'rows': 3}),
            'changed_fields': forms.HiddenInput(),
        }
