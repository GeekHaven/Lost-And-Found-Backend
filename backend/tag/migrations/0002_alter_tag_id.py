# Generated by Django 4.1.3 on 2022-11-08 10:08

from django.db import migrations, models
import tag.models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='id',
            field=models.CharField(default=tag.models.newid, max_length=16, primary_key=True, serialize=False, verbose_name='Unique ID of tag'),
        ),
    ]