# Generated by Django 4.2.9 on 2024-08-16 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('docgen_api', '0005_subcriptionrequestfile'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcriptionrequestfile',
            name='gen_file_path',
            field=models.CharField(default=None, max_length=500),
        ),
    ]
