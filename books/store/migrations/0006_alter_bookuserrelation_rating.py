# Generated by Django 4.2.10 on 2024-02-29 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_book_readers_alter_book_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookuserrelation',
            name='rating',
            field=models.SmallIntegerField(choices=[(1, 'Ok'), (2, 'Fine'), (3, 'Good'), (4, 'Amazing'), (5, 'Incredible')], null=True),
        ),
    ]
