# Generated by Django 4.2.7 on 2025-06-04 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0005_alter_contract_contract_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='company_cnpj',
            field=models.CharField(blank=True, help_text='CNPJ no formato 00.000.000/0000-00', max_length=18, verbose_name='CNPJ da empresa'),
        ),
    ]
