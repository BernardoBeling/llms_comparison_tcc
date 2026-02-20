from django.db import models

class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=models.functions.Now())

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)