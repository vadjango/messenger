# Generated by Django 4.2.6 on 2023-10-31 19:48

from django.db import migrations, models
import django.db.models.deletion
import message_app.chating.models


class Migration(migrations.Migration):

    dependencies = [
        ('message_app_chating', '0003_alter_chat_first_user_alter_chat_second_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to=message_app.chating.models.path_upload_to),
        ),
        migrations.AlterField(
            model_name='message',
            name='chat',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message_app_chating.chat'),
        ),
    ]
