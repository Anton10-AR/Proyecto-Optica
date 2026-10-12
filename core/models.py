from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """Usuario del sistema. Los roles (Vendedor, Almacén, RR.HH., Gerencia) se manejan con Groups."""

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
