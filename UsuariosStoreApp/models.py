from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.utils import timezone
from .choices import PERMISOS
from utils.custom_img import resize_image, crop_image
import uuid
import os


def profile_picture_path(instance, filename):
    random_filename = str(uuid.uuid4())
    extension = os.path.splitext(filename)[1]
    return f"users/{instance.user_FK.username}/{random_filename}{extension}"


# Create your models here.


class Position(models.Model):
    user_position = models.CharField(max_length=45, unique=True)
    permission_code = models.CharField(
        max_length=25, choices=PERMISOS, default="RESTRICTED"
    )

    class Meta:
        db_table = "position"

    def __str__(self):
        return f"{self.user_position}"


class Profile(models.Model):
    last_activity = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(
        upload_to=profile_picture_path, null=True, blank=True, default=None
    )
    telefono_user = models.CharField(max_length=15)
    user_FK = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )
    position_FK = models.ForeignKey(
        Position, on_delete=models.SET_NULL, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        update_last_activity = kwargs.pop("update_last_activity", False)

        if update_last_activity:
            self.last_activity = timezone.now()
            kwargs["update_fields"] = ["last_activity"]

        if self.pk and self.image:
            self.handle_old_image()

        super(Profile, self).save(*args, **kwargs)

        if self.image and os.path.exists(self.image.path):
            resize_image(self.image.path, 300)
            crop_image(self.image.path, 300)

    def update_last_activity(self):
        self.save(update_last_activity=True)

    def handle_old_image(self):
        old_profile = Profile.objects.get(pk=self.pk)
        if old_profile.image and old_profile.image.path != self.image.path:
            default_storage.delete(old_profile.image.path)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"
        ordering = ["-id"]

    def __str__(self):
        return self.user_FK.username
