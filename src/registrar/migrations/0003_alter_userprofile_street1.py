# Generated by Django 4.1.1 on 2022-09-22 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registrar", "0002_alter_userprofile_cc_alter_userprofile_city_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="street1",
            field=models.TextField(blank=True),
        ),
    ]