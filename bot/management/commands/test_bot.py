import json

from bot.tg.schemas import GetUpdateResponse, SendMessageResponse
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_path = settings.BASE_DIR.joinpath('tg_get_response.json')
        send_path = settings.BASE_DIR.joinpath('tg_send_response.json')

        with open(get_path) as f:
            get_data = json.load(f)

            get_resp = GetUpdateResponse(**get_data)
            print(get_resp)

        with open(send_path) as f:
            send_data = json.load(f)
            send_resp = SendMessageResponse(**send_data)
            print(send_resp)