from apps.models import User
from apps.models.users import ProfileModel


class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin '
        verbose_name_plural = 'Admins Users'


class CurrierUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Currier'
        verbose_name_plural = 'Curries'


class OperatorUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Operator'
        verbose_name_plural = 'Operators'


class ManagerUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Manager'
        verbose_name_plural = 'Managers'


class BalanceReport(User):
    class Meta:
        proxy = True
        verbose_name = 'Balance'
        verbose_name_plural = 'Balances'


class OperatorProfile(ProfileModel):
    class Meta:
        proxy = True
        verbose_name = 'Operator Profile'
        verbose_name_plural = 'Operators Profile'
