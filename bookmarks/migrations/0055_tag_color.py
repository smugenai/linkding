from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookmarks", "0054_bookmarkbundle_filter_shared_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tag",
            name="color",
            field=models.CharField(default="#3b82f6", max_length=7),
        ),
    ]
