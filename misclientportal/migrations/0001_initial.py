# Generated by Django 4.2.1 on 2023-05-11 21:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100, verbose_name='Full Name')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('phone_number', models.CharField(max_length=15, verbose_name='Phone Number')),
                ('device_type', models.CharField(max_length=50, verbose_name='Device Type')),
                ('device_model', models.CharField(max_length=50, verbose_name='Device Model')),
                ('issue_description', models.TextField(max_length=500, verbose_name='Issue Description')),
                ('notes', models.TextField(blank=True, max_length=500, null=True, verbose_name='Notes')),
                ('appointment_date', models.DateField(verbose_name='Appointment Date')),
                ('appointment_time', models.TimeField(verbose_name='Appointment Time')),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed')], default='PENDING', max_length=20, verbose_name='Status')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Appointment',
                'verbose_name_plural': 'Appointments',
            },
        ),
    ]