# Generated by Django 4.1.3 on 2022-11-09 07:14

from django.db import migrations, models
import lost.models


class Migration(migrations.Migration):

    dependencies = [
        ('lost', '0006_alter_lost_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lost',
            name='id',
            field=models.CharField(default=lost.models.newid, max_length=10, primary_key=True, serialize=False, verbose_name='Unique ID of lost item'),
        ),
    ]