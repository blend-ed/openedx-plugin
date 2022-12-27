# Generated by Django 2.2.24 on 2021-12-15 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("openedx_plugin_cms", "0003_auto_20211215_0428"),
    ]

    operations = [
        migrations.AddField(
            model_name="courseaudit",
            name="m_external_links",
            field=models.TextField(
                blank=True,
                help_text="A list of all links to sites outside of this Open edX platform installation",
                null=True,
                verbose_name="External Links",
            ),
        ),
        migrations.AlterField(
            model_name="courseaudit",
            name="n_asset_type",
            field=models.TextField(
                blank=True,
                help_text="The kind of file types referenced in any freeform html content in this block. Example: getting-started_x250.png",
                max_length=255,
                null=True,
                verbose_name="Asset Type",
            ),
        ),
    ]