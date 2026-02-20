from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteUserManager(UserManager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class BaseModel(models.Model):
    """
    Base Model (conceitual):
      - id (autoincrement) -> fornecido pelo Django automaticamente (BigAutoField por default)
      - created_at (TIMESTAMP)
      - updated_at (TIMESTAMP)
      - deleted_at (TIMESTAMP, soft delete)
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])


class User(BaseModel, AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cnpj = models.CharField(max_length=32, blank=True, default="")

    # ✅ Incremental: usuário premium
    is_premium = models.BooleanField(default=False)

    objects = SoftDeleteUserManager()
    all_objects = UserManager()

    def __str__(self):
        return f"{self.username} ({self.email})"
