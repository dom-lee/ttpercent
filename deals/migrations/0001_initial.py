# Generated by Django 3.2.5 on 2021-07-27 02:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('category', models.IntegerField(choices=[(1, '부동산 담보대출'), (2, '개인신용'), (3, '스페셜딜'), (4, '기업'), (5, '기타')])),
                ('grade', models.IntegerField(choices=[(1, 'A+'), (2, 'A'), (3, 'A-'), (4, 'B+'), (5, 'B'), (6, 'B-'), (7, 'C+'), (8, 'C'), (9, 'C-'), (10, 'D+'), (11, 'D'), (12, 'D-')])),
                ('earning_rate', models.DecimalField(decimal_places=2, max_digits=4)),
                ('interest_rate', models.DecimalField(decimal_places=2, max_digits=4)),
                ('repayment_period', models.IntegerField()),
                ('repayment_method', models.IntegerField(choices=[(1, '혼합'), (2, '원리금균등'), (3, '만기상환'), (4, '원금균등')])),
                ('net_amount', models.IntegerField()),
                ('repayment_day', models.IntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True)),
                ('reason', models.CharField(max_length=100)),
                ('status', models.IntegerField(choices=[(1, '신청중'), (2, '정상'), (3, '상환지연'), (4, '연체'), (5, '부실'), (6, '정상상환완료'), (7, '부실상환완료'), (8, '모집예정')])),
            ],
            options={
                'db_table': 'deals',
            },
        ),
        migrations.CreateModel(
            name='Debtor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('birth_date', models.DateField()),
            ],
            options={
                'db_table': 'debtors',
            },
        ),
        migrations.CreateModel(
            name='Mortgage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('latitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, max_digits=9)),
                ('estimated_recovery', models.IntegerField()),
                ('appraised_value', models.IntegerField()),
                ('senior_loan_amount', models.IntegerField()),
                ('address', models.TextField()),
                ('completed_date', models.DateField()),
                ('scale', models.CharField(max_length=100)),
                ('supply_area', models.DecimalField(decimal_places=2, max_digits=10)),
                ('using_area', models.DecimalField(decimal_places=2, max_digits=10)),
                ('floors', models.CharField(max_length=100)),
                ('is_usage', models.BooleanField()),
                ('selling_point_title', models.CharField(max_length=100)),
                ('selling_point_description', models.TextField()),
                ('deal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deals.deal')),
            ],
            options={
                'db_table': 'mortgages',
            },
        ),
        migrations.CreateModel(
            name='MortgageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.CharField(max_length=500)),
                ('mortgage', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deals.mortgage')),
            ],
            options={
                'db_table': 'mortgage_images',
            },
        ),
        migrations.AddField(
            model_name='deal',
            name='debtor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='deals.debtor'),
        ),
        migrations.CreateModel(
            name='CreditScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('score', models.IntegerField()),
                ('credit_date', models.DateField()),
                ('debtor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deals.debtor')),
            ],
            options={
                'db_table': 'credit_scores',
            },
        ),
    ]
