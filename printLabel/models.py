# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150, db_collation='Chinese_Taiwan_Stroke_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100, db_collation='Chinese_Taiwan_Stroke_CI_AS')

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    first_name = models.CharField(max_length=150, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    last_name = models.CharField(max_length=150, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    email = models.CharField(max_length=254, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(db_collation='Chinese_Taiwan_Stroke_CI_AS', blank=True, null=True)
    object_repr = models.CharField(max_length=200, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    action_flag = models.SmallIntegerField()
    change_message = models.TextField(db_collation='Chinese_Taiwan_Stroke_CI_AS')
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    model = models.CharField(max_length=100, db_collation='Chinese_Taiwan_Stroke_CI_AS')

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    name = models.CharField(max_length=255, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40, db_collation='Chinese_Taiwan_Stroke_CI_AS')
    session_data = models.TextField(db_collation='Chinese_Taiwan_Stroke_CI_AS')
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Papersetup(models.Model):
    papername = models.CharField(db_column='paperName', primary_key=True, max_length=255, db_collation='Chinese_Taiwan_Stroke_CI_AS')  # Field name made lowercase.       
    paperwidth = models.FloatField(db_column='paperWidth', blank=True, null=True)  # Field name made lowercase.
    paperheight = models.FloatField(db_column='paperHeight', blank=True, null=True)  # Field name made lowercase.
    density = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'paperSetup'