from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('boss', '老板/管理层'),
        ('finance', '财务人员'),
        ('workshop', '车间主管'),
    ]

    real_name = models.CharField('姓名', max_length=20, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='workshop')
    phone = models.CharField('手机号', max_length=11, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.real_name}({self.username})'

    def save(self, *args, **kwargs):
        # Auto-assign boss role to new superusers that haven't had a role set
        if self.is_superuser and not self.pk and self.role == 'workshop':
            self.role = 'boss'
        super().save(*args, **kwargs)
