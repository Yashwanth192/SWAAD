from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_alter_vendor_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='is_available',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='vendor',
            name='is_approved',
            field=models.BooleanField(default=False),
        ),
    ]
