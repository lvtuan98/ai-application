# Generated by Django 4.2.9 on 2024-08-15 09:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import docgen_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('docgen_api', '0004_subcriptionrequest_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubcriptionRequestFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=docgen_api.models.SubcriptionRequestFile.get_new_code, max_length=300)),
                ('file_name', models.CharField(default=None, max_length=300)),
                ('file_path', models.CharField(default=None, max_length=500)),
                ('file_category', models.CharField(default='Origin', max_length=200)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='docgen_api.subcriptionrequest')),
            ],
        ),
    ]
