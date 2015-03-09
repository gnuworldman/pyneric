# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import pyneric.django.db.models.fields.pguuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AutoPgUuidFkTest',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
            options={
                'db_table': 'autopguuidfk',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AutoPgUuidTest',
            fields=[
                ('uuid_field', pyneric.django.db.models.fields.pguuid.AutoPgUuidField(primary_key=True, serialize=False, editable=False)),
            ],
            options={
                'db_table': 'autopguuid',
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL(
            "ALTER TABLE autopguuid ALTER uuid_field SET DEFAULT uuid_generate_v4();",
            "ALTER TABLE autopguuid ALTER uuid_field DROP DEFAULT;"
        ),
        migrations.CreateModel(
            name='FkPatchTest',
            fields=[
                ('auto_field', models.AutoField(primary_key=True, serialize=False, help_text='This is for verifying that ForeignKeys to AutoField are still correct after the ForeignKey.db_type patch.')),
                ('posint_field', models.PositiveSmallIntegerField(unique=True, help_text='This is for verifying that FKs to PositiveSmallIntegerField are still correct after the ForeignKey.db_type patch.')),
            ],
            options={
                'db_table': 'fkpatch',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='autopguuidfktest',
            name='autopguuid',
            field=models.ForeignKey(to='django_test_app.AutoPgUuidTest', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='autopguuidfktest',
            name='fk_auto',
            field=models.ForeignKey(to='django_test_app.FkPatchTest', blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='autopguuidfktest',
            name='fk_posint',
            field=models.ForeignKey(related_name='x', to_field='posint_field', blank=True, null=True, to='django_test_app.FkPatchTest'),
            preserve_default=True,
        ),
    ]
