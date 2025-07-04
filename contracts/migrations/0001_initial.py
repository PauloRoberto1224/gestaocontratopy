# Generated by Django 4.2.7 on 2025-05-27 12:29

import contracts.models
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_number', models.CharField(max_length=100, unique=True, verbose_name='número do contrato')),
                ('title', models.CharField(max_length=200, verbose_name='título')),
                ('description', models.TextField(blank=True, verbose_name='descrição')),
                ('start_date', models.DateField(verbose_name='data de início')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='data de término')),
                ('signature_date', models.DateField(blank=True, null=True, verbose_name='data de assinatura')),
                ('renewal_date', models.DateField(blank=True, null=True, verbose_name='data de renovação')),
                ('value', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='valor total')),
                ('currency', models.CharField(default='BRL', help_text='Código da moeda (ex: BRL, USD, EUR)', max_length=3, verbose_name='moeda')),
                ('document', models.FileField(blank=True, null=True, upload_to=contracts.models.contract_file_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'odt'])], verbose_name='documento')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'contrato',
                'verbose_name_plural': 'contratos',
                'ordering': ['-created_at'],
                'permissions': [('can_export_contracts', 'Pode exportar contratos'), ('can_import_contracts', 'Pode importar contratos'), ('can_approve_contracts', 'Pode aprovar contratos')],
            },
        ),
        migrations.CreateModel(
            name='ContractAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to=contracts.models.contract_attachment_path, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'jpg', 'jpeg', 'png'])], verbose_name='arquivo')),
                ('name', models.CharField(blank=True, max_length=255, verbose_name='nome do arquivo')),
                ('description', models.TextField(blank=True, verbose_name='descrição')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='enviado em')),
                ('file_size', models.PositiveIntegerField(default=0, verbose_name='tamanho do arquivo')),
                ('file_type', models.CharField(blank=True, max_length=50, verbose_name='tipo de arquivo')),
                ('is_public', models.BooleanField(default=False, verbose_name='público')),
            ],
            options={
                'verbose_name': 'anexo de contrato',
                'verbose_name_plural': 'anexos de contrato',
                'ordering': ['-uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='ContractHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_date', models.DateTimeField(auto_now_add=True, verbose_name='data da alteração')),
                ('change_description', models.TextField(verbose_name='descrição da alteração')),
                ('changed_fields', models.JSONField(default=dict, verbose_name='campos alterados')),
            ],
            options={
                'verbose_name': 'histórico de contrato',
                'verbose_name_plural': 'histórico de contratos',
                'ordering': ['-change_date'],
            },
        ),
        migrations.CreateModel(
            name='ContractParty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('client', 'Cliente'), ('supplier', 'Fornecedor'), ('partner', 'Parceiro'), ('other', 'Outro')], default='other', max_length=20, verbose_name='papel')),
                ('is_primary', models.BooleanField(default=False, verbose_name='contato principal')),
                ('notes', models.TextField(blank=True, verbose_name='observações')),
            ],
            options={
                'verbose_name': 'parte do contrato',
                'verbose_name_plural': 'partes do contrato',
            },
        ),
        migrations.CreateModel(
            name='ContractReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='título')),
                ('description', models.TextField(blank=True, verbose_name='descrição')),
                ('due_date', models.DateTimeField(verbose_name='data de vencimento')),
                ('is_completed', models.BooleanField(default=False, verbose_name='concluído')),
                ('completed_date', models.DateTimeField(blank=True, null=True, verbose_name='data de conclusão')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='atualizado em')),
            ],
            options={
                'verbose_name': 'lembrete de contrato',
                'verbose_name_plural': 'lembretes de contrato',
                'ordering': ['due_date'],
            },
        ),
        migrations.CreateModel(
            name='ContractStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nome')),
                ('description', models.TextField(blank=True, verbose_name='descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
                ('color', models.CharField(default='#007bff', help_text='Cor em hexadecimal (ex: #007bff)', max_length=7, verbose_name='cor')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ordem')),
            ],
            options={
                'verbose_name': 'status de contrato',
                'verbose_name_plural': 'status de contratos',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='nome')),
                ('description', models.TextField(blank=True, verbose_name='descrição')),
                ('is_active', models.BooleanField(default=True, verbose_name='ativo')),
            ],
            options={
                'verbose_name': 'tipo de contrato',
                'verbose_name_plural': 'tipos de contrato',
                'ordering': ['name'],
            },
        ),
    ]
