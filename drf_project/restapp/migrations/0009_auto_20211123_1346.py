# Generated by Django 3.2.9 on 2021-11-23 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restapp', '0008_alter_copynote_copy_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='copynote',
            name='copied_from',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='copied_from_story', to='restapp.remote'),
        ),
        migrations.AlterField(
            model_name='copynote',
            name='copied_to',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='copied_to_story', to='restapp.remote'),
        ),
    ]
