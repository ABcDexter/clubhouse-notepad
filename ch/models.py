from django.db import models


class Admin(models.Model):
    """
    Admin is the one creating and editing the link
    -----------------------------------------
    auth(str)  :   Admin auth token
    -----------------------------------------
    """
    auth = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=16, null=True)

    class Meta:
        db_table = 'admin'
        managed = True


class User(models.Model):
    """
    User is the one viewing the link
    -----------------------------------------
    auth(str)  :   User auth token
    -----------------------------------------
    """
    auth = models.CharField(max_length=16, primary_key=True)

    class Meta:
        db_table = 'user'
        managed = True
