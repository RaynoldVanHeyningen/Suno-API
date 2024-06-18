# -*- coding:utf-8 -*-

import json
import os
import time
from http.cookies import SimpleCookie
from threading import Thread

import requests

from utils import COMMON_HEADERS


class SunoCookie:
    def __init__(self, token_file="/mnt/token/token.json"):
        self.cookie = SimpleCookie()
        self.session_id = None
        self.token = None
        self.token_file = token_file
        self.load_token_from_file()

    def load_cookie(self, cookie_str):
        self.cookie.load(cookie_str)

    def get_cookie(self):
        return ";".join([f"{i}={self.cookie.get(i).value}" for i in self.cookie.keys()])

    def set_session_id(self, session_id):
        self.session_id = session_id

    def get_session_id(self):
        return self.session_id

    def get_token(self):
        return self.token

    def set_token(self, token: str):
        self.token = token
        self.save_token_to_file()

    def refresh_token(self):
        headers = {"cookie": self.get_cookie()}
        headers.update(COMMON_HEADERS)
        session_id = self.get_session_id()

        url=f"https://clerk.suno.com/v1/client/sessions/{session_id}/tokens?_clerk_js_version=4.72.0-snapshot.vc141245",
        # headers = {
        #     "Content-Type": "application/json",
        #     "Cookie": self.get_cookie(),
        #     # Add any other headers required for the request
        # }
        # data = {
        #     # Add any data required for the request
        # }
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            resp_headers = dict(response.headers)
            set_cookie = resp_headers.get("Set-Cookie")
            self.load_cookie(set_cookie)
            token = response.json().get("jwt")

            self.set_token(token)

            print(set_cookie)
            print(f"*** token -> {token} ***")
        else:
            raise Exception("Failed to refresh token")
    
    def save_token_to_file(self):
        with open(self.token_file, "w") as f:
            json.dump({"token": self.token}, f)
    
    def load_token_from_file(self):
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                data = json.load(f)
                self.token = data.get("token")


suno_auth = SunoCookie()
suno_auth.set_session_id(os.getenv("SESSION_ID"))
suno_auth.load_cookie(os.getenv("COOKIE"))


def update_token(suno_cookie: SunoCookie):
    headers = {"cookie": suno_cookie.get_cookie()}
    headers.update(COMMON_HEADERS)
    session_id = suno_cookie.get_session_id()

    resp = requests.post(
        url=f"https://clerk.suno.com/v1/client/sessions/{session_id}/tokens?_clerk_js_version=4.72.0-snapshot.vc141245",
        headers=headers,
    )

    resp_headers = dict(resp.headers)
    set_cookie = resp_headers.get("Set-Cookie")
    suno_cookie.load_cookie(set_cookie)
    token = resp.json().get("jwt")
    suno_cookie.set_token(token)
    # print(set_cookie)
    # print(f"*** token -> {token} ***")


def keep_alive(suno_cookie: SunoCookie):
    while True:
        try:
            update_token(suno_cookie)
        except Exception as e:
            print(e)
        finally:
            time.sleep(5)


def start_keep_alive(suno_cookie: SunoCookie):
    t = Thread(target=keep_alive, args=(suno_cookie,))
    t.start()


start_keep_alive(suno_auth)
