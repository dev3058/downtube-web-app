# Generated by Django 4.0.3 on 2022-04-27 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_popularchannel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='popularchannel',
            old_name='channel_videoId',
            new_name='channel_video_link',
        ),
    ]
