from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Article, Category, Comment, CustomUser, EmailConfirmation


MODEL_NAMES = {
    CustomUser: "пользователь",
    Category: "категория",
    Article: "статья",
    EmailConfirmation: "подтверждение email",
    Comment: "комментарий",
}


@receiver(post_save, sender=CustomUser)
@receiver(post_save, sender=Category)
@receiver(post_save, sender=Article)
@receiver(post_save, sender=EmailConfirmation)
@receiver(post_save, sender=Comment)
def object_saved(sender, instance, created, **kwargs):
    action = "Создан объект" if created else "Обновлён объект"
    print(f"[SIGNAL] {action}: {MODEL_NAMES[sender]} — {instance}")


@receiver(pre_delete, sender=CustomUser)
@receiver(pre_delete, sender=Category)
@receiver(pre_delete, sender=Article)
@receiver(pre_delete, sender=EmailConfirmation)
@receiver(pre_delete, sender=Comment)
def object_deleting(sender, instance, **kwargs):
    print(f"[SIGNAL] Удаляется объект: {MODEL_NAMES[sender]} — {instance}")