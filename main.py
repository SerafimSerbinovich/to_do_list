from typing import Callable, Any

from pydantic import BaseModel


class FSM(BaseModel):
    next_handler: Callable
    data: dict[str, Any] = {}


users: dict[int, FSM] = {}

CATEGORIES = ("ONE", "TWO", "THREE")


def main(chat_id, msg):
    if msg == '/create':
        handler_create_goal_command(chat_id, msg)
    elif msg == '/cancel':
        users.pop(chat_id, None)
    elif chat_id in users:
        users[chat_id].next_handler(chat_id, msg)


def handler_create_goal_command(chat_id, msg):
    users[chat_id] = FSM(next_handler=second_handler)


def second_handler(chat_id, msg):
    cat = CATEGORIES[int(msg)]
    users[chat_id].data.update({'category': cat})

    print('select category')

    print('set title')
    users[chat_id].next_handler = third_handler


def third_handler(chat_id, msg):
    cat = users[chat_id].data['category']
    print(f'goal created with category {cat}, title={msg}')
    users.pop(chat_id, None)
