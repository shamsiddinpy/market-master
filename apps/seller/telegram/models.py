from django.db.models import CharField, CASCADE, DateTimeField, Model, OneToOneField


# Create your models here.
class UserBot(Model):
    user = OneToOneField('websayt.User', on_delete=CASCADE)
    token = CharField(max_length=255)
    bot_name = CharField(max_length=100)
    bot_username = CharField(max_length=100)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s bot: {self.bot_name}"

