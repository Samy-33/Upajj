# Generated by Django 2.1.7 on 2019-03-02 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(blank=True, default='', max_length=50)),
                ('season', models.CharField(blank=True, default='', max_length=50)),
                ('crop', models.CharField(blank=True, default='', max_length=50)),
                ('context', models.TextField(max_length=1000, null=True)),
            ],
        ),
    ]