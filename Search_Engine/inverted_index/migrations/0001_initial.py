# Generated by Django 2.0.2 on 2018-03-07 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('word', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('path', models.CharField(max_length=2000)),
            ],
        ),
    ]
