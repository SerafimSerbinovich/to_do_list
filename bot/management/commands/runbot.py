
from typing import Callable, Any

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.schemas import Message
from django.conf import settings
from django.core.management import BaseCommand
from goals.models import Goal, GoalCategory
from pydantic import BaseModel


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient(settings.BOT_TOKEN)
        self.users_data = {}

    def handle(self, *args, **options):
        offset = 0
        self.stdout.write(self.style.SUCCESS('Bot started...'))
        while True:
            res = self.tg_client.get_updates(offset=offset, allowed_updates='message')
            for item in res.result:
                offset = item.update_id + 1
                self.handle_message(item.message)

    def handle_message(self, message: Message):
        tg_user, _ = TgUser.objects.get_or_create(chat_id=message.chat.id, defaults={'username': message.chat.username})
        if not tg_user.is_verified:
            tg_user.update_verification_code()
            self.tg_client.send_message(message.chat.id, f'Verification code: {tg_user.verification_code}')
        else:
            self.handle_auth_user(tg_user, message)

    def handle_auth_user(self, tg_user: TgUser, message: Message):
        commands: list = ['/goals', '/create', '/cancel']
        create_chat: dict | None = self.users_data.get(message.chat.id, None)
        self.tg_client.send_message(
            chat_id=message.chat.id,
            text=f'Доступные команды:\n/goals\n/create\n/cancel '
        )

        if message.text == '/cancel':
            self.users_data.pop(message.chat.id, None)
            create_chat = None
            self.tg_client.send_message(chat_id=message.chat.id, text='Operation was cancelled')

        if message.text in commands and not create_chat:
            if message.text == '/goals':
                qs = Goal.objects.filter(category__is_deleted=False, category__board__participants__user_id=tg_user.user.id
                                         ).exclude(status=Goal.Status.archived)

                goals = [f'{goal.id} - {goal.title}' for goal in qs]
                self.tg_client.send_message(chat_id=message.chat.id, text='No goals' if not goals else '\n'.join(goals))

            if message.text == '/create':
                categories_qs = GoalCategory.objects.filter(
                    board__participants__user_id=tg_user.user.id, is_deleted=False
                )

                categories = []
                categories_id = []
                for category in categories_qs:
                    categories.append(f'{category.id} - {category.title}')
                    categories_id.append(str(category.id))

                self.tg_client.send_message(
                    chat_id=message.chat.id, text=f'Выберите номер категории:\n' + '\n'.join(categories)
                )
                self.users_data[message.chat.id] = {
                    'categories': categories,
                    'categories_id': categories_id,
                    'category_id': '',
                    'goal_title': '',
                    'stage': 1,
                }

        if message.text not in commands and create_chat:
            if create_chat['stage'] == 2:
                Goal.objects.create(
                    user_id=tg_user.user.id,
                    category_id=int(self.users_data[message.chat.id]['category_id']),
                    title=message.text,
                )
                self.tg_client.send_message(chat_id=message.chat.id, text='Цель сохранена')
                self.users_data.pop(message.chat.id, None)

            elif create_chat['stage'] == 1:
                if message.text == '/cancel':
                    self.users_data.pop(message.chat.id, None)
                    create_chat = None
                    self.tg_client.send_message(chat_id=message.chat.id, text='Операция отменена')

                if message.text in create_chat.get('categories_id', []):
                    self.tg_client.send_message(chat_id=message.chat.id, text='Введите название цели')
                    self.users_data[message.chat.id] = {'category_id': message.text, 'stage': 2}
                else:
                    self.tg_client.send_message(
                        chat_id=message.chat.id,
                        text='Введен неправильный номер категории\n' + '\n'.join(create_chat.get('категории', [])),
                    )

        if message.text not in commands and not create_chat:
            self.tg_client.send_message(chat_id=message.chat.id, text=f'Неизвестная команда')

    def handle_unauthorized_user(self, tg_user: TgUser, msg: Message):
        """
        Функция обработки сообщений ек авторизованных пользователей.
        Генерирует код для верификации на сайте
        """
        code = tg_user._generate_verification_code()
        tg_user.verification_code = code
        tg_user.save()

        self.tg_client.send_message(chat_id=msg.chat.id, text=f'Ваш код верификации: {code}')
