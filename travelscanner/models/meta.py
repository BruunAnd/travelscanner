from datetime import datetime
from peewee import Model, DateTimeField, TextField
from travelscanner.data.database import Database


class MetaModel(Model):
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(MetaModel, self).save(*args, **kwargs)

    class Meta:
        database = Database.get_driver()


class CrawledModel(MetaModel):
    data_dump = TextField(null=True)
