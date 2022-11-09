# Generated by Django 4.1.3 on 2022-11-08 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tag', '0002_alter_tag_id'),
        ('lost', '0004_lost_tag'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lost',
            name='tag',
        ),
        migrations.AddField(
            model_name='lost',
            name='tag',
            field=models.ManyToManyField(to='tag.tag'),
        ),
    ]
