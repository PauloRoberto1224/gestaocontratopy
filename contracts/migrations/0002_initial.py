# Generated by Django 4.2.7 on 2025-05-27 12:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contractreminder',
            name='assigned_to',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_reminders', to=settings.AUTH_USER_MODEL, verbose_name='atribuído a'),
        ),
        migrations.AddField(
            model_name='contractreminder',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='contracts.contract', verbose_name='contrato'),
        ),
        migrations.AddField(
            model_name='contractreminder',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_reminders', to=settings.AUTH_USER_MODEL, verbose_name='criado por'),
        ),
        migrations.AddField(
            model_name='contractparty',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contract_parties', to='contracts.contract', verbose_name='contrato'),
        ),
        migrations.AddField(
            model_name='contractparty',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contract_parties', to=settings.AUTH_USER_MODEL, verbose_name='usuário'),
        ),
        migrations.AddField(
            model_name='contracthistory',
            name='changed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_changes', to=settings.AUTH_USER_MODEL, verbose_name='alterado por'),
        ),
        migrations.AddField(
            model_name='contracthistory',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history_entries', to='contracts.contract', verbose_name='contrato'),
        ),
        migrations.AddField(
            model_name='contractattachment',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='contracts.contract', verbose_name='contrato'),
        ),
        migrations.AddField(
            model_name='contractattachment',
            name='uploaded_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_attachments', to=settings.AUTH_USER_MODEL, verbose_name='enviado por'),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='contracts.contracttype', verbose_name='tipo de contrato'),
        ),
        migrations.AddField(
            model_name='contract',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_contracts', to=settings.AUTH_USER_MODEL, verbose_name='criado por'),
        ),
        migrations.AddField(
            model_name='contract',
            name='parties',
            field=models.ManyToManyField(related_name='contracts_as_party', through='contracts.ContractParty', to=settings.AUTH_USER_MODEL, verbose_name='partes envolvidas'),
        ),
        migrations.AddField(
            model_name='contract',
            name='responsible',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='managed_contracts', to=settings.AUTH_USER_MODEL, verbose_name='responsável'),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contracts', to='contracts.contractstatus', verbose_name='status'),
        ),
        migrations.AlterUniqueTogether(
            name='contractparty',
            unique_together={('contract', 'user')},
        ),
    ]
