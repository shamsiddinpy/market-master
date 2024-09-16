from django.db.models import Manager

from apps.websayt.models import User
from apps.websayt.models.products import Order


class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Admin '
        verbose_name_plural = 'Admin Users'


class CurrierUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Currier'
        verbose_name_plural = 'Currie Users'


class OperatorUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Operator'
        verbose_name_plural = 'Operator Users'


class ManagerUser(User):
    class Meta:
        proxy = True
        verbose_name = 'Manager'
        verbose_name_plural = 'Manager Users'


class BalanceReport(User):
    class Meta:
        proxy = True
        verbose_name = 'Balance'
        verbose_name_plural = 'Balances'


"""Order"""


class StatusOrder(Manager):
    def for_status(self, status):
        return self.get_queryset().filter(status=status)


class NewOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.NEW)


class NewOrders(Order):
    object = NewOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'New Order'
        verbose_name_plural = 'New Orders'


"""Visit"""


class VisitOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.VISIT)


class VisitOrders(Order):
    object = VisitOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Visit Order'
        verbose_name_plural = 'Visit Orders'


"""Ready"""


class ReadyOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.READY)


class ReadyOrders(Order):
    object = ReadyOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Ready Order'
        verbose_name_plural = 'Ready Orders'


"""Delivrey"""


class DelivreyOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.DELIVERY)


class DeliveryOrders(Order):
    object = DelivreyOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivery Order'
        verbose_name_plural = 'Delivery Orders'


"""Delivered"""


class DeliveredOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.DELIVERED)


class DeliveredOrders(Order):
    object = DeliveredOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Delivered Order'
        verbose_name_plural = 'Delivered Orders'


"""Canceled"""


class CanceledOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.CANCELED)


class CanceledOrders(Order):
    object = CanceledOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Canceled Order'
        verbose_name_plural = 'Canceled Orders'


"""Archived"""


class ArchivedOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.ARCHIVED)


class ArchivedOrders(Order):
    object = ArchivedOrderManager()

    class Meta:
        proxy = True
        verbose_name = 'Archived Order'
        verbose_name_plural = 'Archived Orders'


"""Phone"""


class PhoneOrderManager(StatusOrder):
    def get_queryset(self):
        return super().get_queryset().filter(status=Order.Status.PHONE)


class PhoneOrder(Order):
    class Meta:
        proxy = True
        verbose_name = 'Missed Call Order'
        verbose_name_plural = 'Missed Call Orders'
