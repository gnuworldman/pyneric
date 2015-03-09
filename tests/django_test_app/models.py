# -*- coding: utf-8 -*-
"""Models for django_test_app."""

from django.db import models

from pyneric.django.db.models.fields import pguuid


class AutoPgUuidTest(models.Model):

    uuid_field = pguuid.AutoPgUuidField(primary_key=True)

    class Meta:

        db_table = 'autopguuid'


class FkPatchTest(models.Model):

    auto_field = models.AutoField(
        primary_key=True,
        help_text="This is for verifying that ForeignKeys to AutoField"
                  " are still correct after the ForeignKey.db_type patch.")
    posint_field = models.PositiveSmallIntegerField(
        unique=True,
        help_text="This is for verifying that FKs to PositiveSmallIntegerField"
                  " are still correct after the ForeignKey.db_type patch.")

    class Meta:

        db_table = 'fkpatch'


class AutoPgUuidFkTest(models.Model):

    autopguuid = models.ForeignKey(AutoPgUuidTest, blank=True, null=True)
    fk_auto = models.ForeignKey(FkPatchTest, blank=True, null=True)
    fk_posint = models.ForeignKey(FkPatchTest, blank=True, null=True,
                                  to_field='posint_field', related_name='x')

    class Meta:

        db_table = 'autopguuidfk'
