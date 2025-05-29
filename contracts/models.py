from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.validators import MinValueValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import os


def contract_file_path(instance, filename):
    """Gera o caminho para armazenar os arquivos de contrato"""
    ext = filename.split('.')[-1]
    filename = f"contract_{instance.id}.{ext}"
    return os.path.join('contracts', str(instance.id), filename)


class ContractStatus(models.Model):
    """Modelo para status dos contratos"""
    name = models.CharField(_('nome'), max_length=100, unique=True)
    description = models.TextField(_('descrição'), blank=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    color = models.CharField(_('cor'), max_length=7, default='#007bff',
                           help_text=_('Cor em hexadecimal (ex: #007bff)'))
    order = models.PositiveIntegerField(_('ordem'), default=0)
    
    class Meta:
        verbose_name = _('status de contrato')
        verbose_name_plural = _('status de contratos')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class ContractType(models.Model):
    """Modelo para tipos de contrato"""
    name = models.CharField(_('nome'), max_length=100, unique=True)
    description = models.TextField(_('descrição'), blank=True)
    is_active = models.BooleanField(_('ativo'), default=True)
    
    class Meta:
        verbose_name = _('tipo de contrato')
        verbose_name_plural = _('tipos de contrato')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Contract(models.Model):
    """Modelo principal para contratos"""
    # Informações básicas
    contract_number = models.CharField(
        _('número do contrato'),
        max_length=20,
        unique=True,
        blank=True,
        help_text=_('Número do contrato no formato CTR-YYYY-NNN')
    )
    
    @classmethod
    def get_next_contract_number(cls):
        """Gera o próximo número de contrato no formato CTR-YYYY-NNN"""
        from django.db.models import Max
        from django.utils import timezone
        
        current_year = timezone.now().year
        
        # Busca o maior número de sequência para o ano atual
        last_contract = cls.objects.filter(
            contract_number__startswith=f'CTR-{current_year}-'
        ).order_by('-contract_number').first()
        
        if last_contract:
            try:
                # Extrai o número de sequência e incrementa
                last_number = int(last_contract.contract_number.split('-')[-1])
                next_number = last_number + 1
            except (IndexError, ValueError):
                next_number = 1
        else:
            next_number = 1
            
        return f'CTR-{current_year}-{next_number:03d}'
    
    def save(self, *args, **kwargs):
        # Gera o número do contrato se não existir
        if not self.contract_number:
            self.contract_number = self.get_next_contract_number()
        
        # Garante que o número do contrato está no formato correto
        if not self.contract_number.startswith('CTR-'):
            self.contract_number = self.get_next_contract_number()
            
        super().save(*args, **kwargs)
    title = models.CharField(_('título'), max_length=200, null=True, blank=True, help_text=_('Título do contrato (obsoleto, usar campo empresa)'))
    company = models.CharField(_('empresa'), max_length=200, default='Empresa não informada')
    fiscal_name = models.CharField(_('nome fiscal'), max_length=200, default='Fiscal não informado')
    fiscal_registration = models.CharField(_('matrícula do fiscal'), max_length=7, 
                                         help_text=_('Matrícula com 7 dígitos'), default='0000000')
    alternate_fiscal_name = models.CharField(_('nome do fiscal suplente'), max_length=200, blank=True, 
                                           default='')
    alternate_fiscal_registration = models.CharField(_('matrícula do fiscal suplente'), max_length=7, 
                                                    blank=True, default='',
                                                    help_text=_('Matrícula com 7 dígitos'))
    
    # Termo do contrato
    TERM_CHOICES = [
        ('initial', 'Contrato Inicial'),
        ('term_1', '1º Termo Aditivo'),
        ('term_2', '2º Termo Aditivo'),
        ('term_3', '3º Termo Aditivo'),
        ('term_4', '4º Termo Aditivo'),
        ('term_5', '5º Termo Aditivo'),
    ]
    contract_term = models.CharField(
        _('termo do contrato'),
        max_length=10,
        choices=TERM_CHOICES,
        default='initial'
    )
    
    # Documentos
    contract_document = models.FileField(
        _('contrato'),
        upload_to=contract_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    fiscal_portaria = models.FileField(
        _('portaria do fiscal'),
        upload_to=contract_file_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    additive_term = models.FileField(
        _('termo aditivo'),
        upload_to=contract_file_path,
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    
    # Observações
    notes = models.TextField(_('observações'), blank=True)
    
    # Relacionamentos
    status = models.ForeignKey(
        ContractStatus,
        on_delete=models.PROTECT,
        verbose_name=_('status'),
        related_name='contracts',
        default=1  # Você pode precisar ajustar este valor padrão
    )
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name=_('responsável'),
        related_name='managed_contracts',
        null=True,
        blank=True
    )
    
    # Datas importantes
    start_date = models.DateField(_('data de início'))
    end_date = models.DateField(_('data de término'))
    
    # Valores financeiros
    value = models.DecimalField(
        _('valor total'),
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    currency = models.CharField(
        _('moeda'),
        max_length=3,
        default='BRL',
        help_text=_('Código da moeda (ex: BRL, USD, EUR)')
    )
    
    # Anexos
    document = models.FileField(
        _('documento'),
        upload_to=contract_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'odt'])
        ],
        null=True,
        blank=True
    )
    
    # Metadados
    is_active = models.BooleanField(_('ativo'), default=True)
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_contracts',
        verbose_name=_('criado por')
    )
    
    class Meta:
        verbose_name = _('contrato')
        verbose_name_plural = _('contratos')
        ordering = ['-created_at']
        permissions = [
            ('can_export_contracts', 'Pode exportar contratos'),
            ('can_import_contracts', 'Pode importar contratos'),
            ('can_approve_contracts', 'Pode aprovar contratos'),
        ]
    
    def __str__(self):
        return f"{self.contract_number} - {self.title}"
    
    def clean(self):
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({
                'end_date': _('A data de término não pode ser anterior à data de início.')
            })
    
    @property
    def is_expired(self):
        if not self.end_date:
            return False
        return self.end_date < timezone.now().date()
    
    @property
    def days_until_expiration(self):
        if not self.end_date:
            return None
        delta = self.end_date - timezone.now().date()
        return delta.days


class ContractParty(models.Model):
    """Modelo para representar as partes envolvidas em um contrato"""
    ROLE_CHOICES = [
        ('client', _('Cliente')),
        ('supplier', _('Fornecedor')),
        ('partner', _('Parceiro')),
        ('other', _('Outro')),
    ]
    
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name=_('contrato'),
        related_name='contract_parties'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('usuário'),
        related_name='contract_parties'
    )
    role = models.CharField(
        _('papel'),
        max_length=20,
        choices=ROLE_CHOICES,
        default='other'
    )
    is_primary = models.BooleanField(_('contato principal'), default=False)
    notes = models.TextField(_('observações'), blank=True)
    
    class Meta:
        verbose_name = _('parte do contrato')
        verbose_name_plural = _('partes do contrato')
        unique_together = ('contract', 'user')
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} em {self.contract}"


class ContractHistory(models.Model):
    """Modelo para registrar o histórico de alterações nos contratos"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name=_('contrato'),
        related_name='history_entries'
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('alterado por'),
        related_name='contract_changes'
    )
    change_date = models.DateTimeField(_('data da alteração'), auto_now_add=True)
    change_description = models.TextField(_('descrição da alteração'))
    changed_fields = models.JSONField(_('campos alterados'), default=dict)
    
    class Meta:
        verbose_name = _('histórico de contrato')
        verbose_name_plural = _('histórico de contratos')
        ordering = ['-change_date']
    
    def __str__(self):
        return f"Alteração em {self.contract} por {self.changed_by} em {self.change_date}"


class ContractReminder(models.Model):
    """Modelo para lembretes relacionados a contratos"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name=_('contrato'),
        related_name='reminders'
    )
    title = models.CharField(_('título'), max_length=200)
    description = models.TextField(_('descrição'), blank=True)
    due_date = models.DateTimeField(_('data de vencimento'))
    is_completed = models.BooleanField(_('concluído'), default=False)
    completed_date = models.DateTimeField(_('data de conclusão'), null=True, blank=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('atribuído a'),
        related_name='contract_reminders'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reminders',
        verbose_name=_('criado por')
    )
    created_at = models.DateTimeField(_('criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('lembrete de contrato')
        verbose_name_plural = _('lembretes de contrato')
        ordering = ['due_date']

    def __str__(self):
        return f"{self.title} - {self.contract}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_date:
            self.completed_date = timezone.now()
        elif not self.is_completed:
            self.completed_date = None
        super().save(*args, **kwargs)


def contract_attachment_path(instance, filename):
    """Gera o caminho para armazenar os anexos de contrato"""
    return f'contracts/{instance.contract.id}/attachments/{int(timezone.now().timestamp())}_{filename}'


class ContractAttachment(models.Model):
    """Modelo para anexos de contratos"""
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        verbose_name=_('contrato'),
        related_name='attachments'
    )
    file = models.FileField(
        _('arquivo'),
        upload_to=contract_attachment_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png']
            )
        ]
    )
    name = models.CharField(_('nome do arquivo'), max_length=255, blank=True)
    description = models.TextField(_('descrição'), blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('enviado por'),
        related_name='uploaded_attachments'
    )
    uploaded_at = models.DateTimeField(_('enviado em'), auto_now_add=True)
    file_size = models.PositiveIntegerField(_('tamanho do arquivo'), default=0)
    file_type = models.CharField(_('tipo de arquivo'), max_length=50, blank=True)
    is_public = models.BooleanField(_('público'), default=False)

    class Meta:
        verbose_name = _('anexo de contrato')
        verbose_name_plural = _('anexos de contrato')
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.name or os.path.basename(self.file.name)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)

        if self.file:
            self.file_size = self.file.size
            self.file_type = os.path.splitext(self.file.name)[1].lower().lstrip('.')

        super().save(*args, **kwargs)

    def get_file_extension(self):
        """Retorna a extensão do arquivo em minúsculas"""
        return os.path.splitext(self.file.name)[1].lower().lstrip('.')

    def get_file_size(self):
        """Retorna o tamanho do arquivo formatado"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} TB"
