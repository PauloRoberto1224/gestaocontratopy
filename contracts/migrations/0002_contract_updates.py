from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

def create_default_status(apps, schema_editor):
    ContractStatus = apps.get_model('contracts', 'ContractStatus')
    ContractStatus.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Ativo',
            'description': 'Contrato ativo',
            'is_active': True,
            'color': '#28a745',
            'order': 1
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_status, reverse_code=migrations.RunPython.noop),
        
        # Add new fields to Contract model
        migrations.AddField(
            model_name='contract',
            name='additive_term',
            field=models.FileField(blank=True, null=True, upload_to='contracts/%Y/%m/%d/', verbose_name='termo aditivo'),
        ),
        migrations.AddField(
            model_name='contract',
            name='alternate_fiscal_name',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='nome do fiscal suplente'),
        ),
        migrations.AddField(
            model_name='contract',
            name='alternate_fiscal_registration',
            field=models.CharField(blank=True, default='', help_text='Matrícula com 7 dígitos', max_length=7, verbose_name='matrícula do fiscal suplente'),
        ),
        migrations.AddField(
            model_name='contract',
            name='company',
            field=models.CharField(default='Empresa não informada', max_length=200, verbose_name='empresa'),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_document',
            field=models.FileField(upload_to='contracts/%Y/%m/%d/', verbose_name='contrato'),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_term',
            field=models.CharField(choices=[('initial', 'Contrato Inicial'), ('term_1', '1º Termo Aditivo'), ('term_2', '2º Termo Aditivo'), ('term_3', '3º Termo Aditivo'), ('term_4', '4º Termo Aditivo'), ('term_5', '5º Termo Aditivo')], default='initial', max_length=10, verbose_name='termo do contrato'),
        ),
        migrations.AddField(
            model_name='contract',
            name='fiscal_name',
            field=models.CharField(default='Fiscal não informado', max_length=200, verbose_name='nome fiscal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='fiscal_portaria',
            field=models.FileField(upload_to='contracts/%Y/%m/%d/', verbose_name='portaria do fiscal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='fiscal_registration',
            field=models.CharField(default='0000000', help_text='Matrícula com 7 dígitos', max_length=7, verbose_name='matrícula do fiscal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='notes',
            field=models.TextField(blank=True, verbose_name='observações'),
        ),
        
        # Update existing fields
        migrations.AlterField(
            model_name='contract',
            name='contract_number',
            field=models.CharField(default='TEMP-000', max_length=100, unique=True, verbose_name='número do contrato'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='end_date',
            field=models.DateField(verbose_name='data de término'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='contracts.contractstatus', verbose_name='status'),
        ),
        migrations.AlterField(
            model_name='contract',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(0)], verbose_name='valor total'),
        ),
    ]
