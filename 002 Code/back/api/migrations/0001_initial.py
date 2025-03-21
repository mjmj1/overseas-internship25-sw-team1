# Generated by Django 5.1.6 on 2025-02-25 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AssignTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('CourseCode', models.CharField(max_length=20)),
                ('ResourceCode', models.CharField(max_length=20)),
                ('FacultyCode', models.CharField(max_length=20)),
                ('Session', models.CharField(max_length=255)),
                ('Lecturer', models.CharField(max_length=255)),
                ('CombineBy', models.CharField(max_length=50)),
                ('DayOfWeek', models.CharField(max_length=10)),
                ('RoomCapacity', models.IntegerField()),
                ('CourseCapacity', models.IntegerField()),
                ('StartTime', models.IntegerField()),
                ('MinPerSession', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ChildCourseOffer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('FatherCode', models.CharField(max_length=20)),
                ('CourseCode', models.CharField(max_length=20)),
                ('Capacity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ExceptionCourseOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CourseCode', models.CharField(max_length=20)),
                ('FacultyCode', models.CharField(max_length=20)),
                ('Session', models.CharField(max_length=255)),
                ('Capacity', models.IntegerField()),
                ('MinPerSession', models.IntegerField()),
                ('Lecturer', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='FatherCourseOffer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('CourseCode', models.CharField(max_length=20)),
                ('FacultyCode', models.CharField(max_length=20)),
                ('Session', models.CharField(max_length=255)),
                ('Capacity', models.IntegerField()),
                ('MinPerSession', models.IntegerField()),
                ('Lecturer', models.CharField(max_length=255)),
                ('CourseType', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='NotGeneratedTable',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('CourseCode', models.CharField(max_length=20)),
                ('FacultyCode', models.CharField(max_length=20)),
                ('Session', models.CharField(max_length=255)),
                ('Reason', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ResourceRoom',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ResourceCode', models.CharField(max_length=100)),
                ('Description', models.CharField(max_length=255)),
                ('Capacity', models.IntegerField()),
                ('Lecture', models.CharField(max_length=1)),
                ('Tutorial', models.CharField(max_length=1)),
                ('Lab', models.CharField(max_length=1)),
                ('Group', models.CharField(max_length=1)),
                ('Clinic', models.CharField(max_length=1)),
                ('PBL', models.CharField(max_length=1)),
                ('Kitchen', models.CharField(max_length=1)),
                ('Drawing', models.CharField(max_length=1)),
                ('Imus', models.CharField(max_length=10)),
            ],
        ),
    ]
