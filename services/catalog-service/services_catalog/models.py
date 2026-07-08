import uuid
from django.db import models


class Service(models.Model):
    id        = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name      = models.CharField(max_length=80)
    category  = models.CharField(max_length=30)
    price     = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'services'
