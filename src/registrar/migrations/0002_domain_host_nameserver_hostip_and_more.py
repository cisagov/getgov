# Generated by Django 4.1.3 on 2022-11-28 19:07

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_fsm  # type: ignore


class Migration(migrations.Migration):

    dependencies = [
        ("registrar", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Domain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="Fully qualified domain name",
                        max_length=253,
                    ),
                ),
                (
                    "is_active",
                    django_fsm.FSMField(
                        choices=[(True, "Yes"), (False, "No")],
                        default=False,
                        help_text="Domain is live in the registry",
                        max_length=50,
                    ),
                ),
                ("owners", models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        default=None,
                        help_text="Fully qualified domain name",
                        max_length=253,
                        unique=True,
                    ),
                ),
                (
                    "domain",
                    models.ForeignKey(
                        help_text="Domain to which this host belongs",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="host",
                        to="registrar.domain",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Nameserver",
            fields=[
                (
                    "host_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="registrar.host",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("registrar.host",),
        ),
        migrations.CreateModel(
            name="HostIP",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "address",
                    models.CharField(
                        default=None,
                        help_text="IP address",
                        max_length=46,
                        validators=[django.core.validators.validate_ipv46_address],
                    ),
                ),
                (
                    "host",
                    models.ForeignKey(
                        help_text="Host to which this IP address belongs",
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ip",
                        to="registrar.host",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="domainapplication",
            name="requested_domain",
            field=models.OneToOneField(
                blank=True,
                help_text="The requested domain",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="domain_application",
                to="registrar.domain",
            ),
        ),
        migrations.AddConstraint(
            model_name="domain",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_active", True)),
                fields=("name",),
                name="unique_domain_name_in_registry",
            ),
        ),
    ]