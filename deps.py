# -*- coding:utf-8 -*-

from cookie import suno_auth


def get_token():
    try:
        yield suno_auth.get_token()
    finally:
        pass
