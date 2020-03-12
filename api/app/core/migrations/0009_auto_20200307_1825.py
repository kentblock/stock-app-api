# Generated by Django 3.0.3 on 2020-03-07 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20200302_0503'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyprice',
            name='high_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='low_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='open_price',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='time_stamp',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='dailyprice',
            name='volume',
            field=models.IntegerField(default=69),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stock',
            name='latest_price_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='stock',
            name='ticker',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
