# Generated by Django 5.1 on 2024-11-22 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Название'),
        ),
    ]