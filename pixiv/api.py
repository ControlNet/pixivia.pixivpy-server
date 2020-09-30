import json
from json.decoder import JSONDecodeError

from pixivpy3 import PixivAPI
from pixivpy3.utils import JsonDict

from pixiv.validation import handle_auth_validation


class API:
    def __init__(self, pixiv_account: str, pixiv_password: str, token_path: str, image_saving_dir: str):
        self.api = PixivAPI()
        self.pixiv_account = pixiv_account
        self.pixiv_password = pixiv_password
        self.token_path = token_path
        self.image_saving_dir = image_saving_dir

    def login_or_load_token(self, try_token=True) -> str:
        if try_token:
            try:
                with open(self.token_path, "r", encoding="UTF-8") as token_file:
                    token = json.load(token_file)
            except FileNotFoundError:
                has_token = False
            except JSONDecodeError:
                has_token = False
            else:
                has_token = True
        else:
            has_token = False

        if has_token:
            response = self.api.set_auth(token["access_token"], token["refresh_token"])
        else:
            response = self.api.login(self.pixiv_account, self.pixiv_password)

        # save token
        self.save_token()
        return response

    def save_token(self):
        with open(self.token_path, "w", encoding="UTF-8") as token_file:
            token_file.write(json.dumps({
                "access_token": self.api.access_token,
                "refresh_token": self.api.refresh_token
            }))

    @handle_auth_validation
    def works(self, illust_id: int, include_sanity_level: bool = False) -> JsonDict:
        return self.api.works(illust_id=illust_id, include_sanity_level=include_sanity_level)

    @handle_auth_validation
    def download(self, url, prefix="", name=None, replace=False, fname=None,
                 referer='https://app-api.pixiv.net/') -> bool:
        return self.api.download(url, prefix=prefix, path=self.image_saving_dir, name=name, replace=replace,
                                 fname=fname,
                                 referer=referer)

    @handle_auth_validation
    def me_following_works(self, page=1, per_page=30,
                           image_sizes=None,
                           include_stats=True, include_sanity_level=True):
        if image_sizes is None:
            image_sizes = ['px_128x128', 'px_480mw', 'large']
        return self.api.me_following_works(page, per_page, image_sizes, include_stats, include_sanity_level)

    @handle_auth_validation
    def me_following(self, page=1, per_page=30, publicity='public'):
        return self.api.me_following(page=page, per_page=per_page, publicity=publicity)

    @handle_auth_validation
    def follow(self, user_id: int):
        return self.api.me_favorite_users_follow(user_id)["status"]

    @handle_auth_validation
    def unfollow(self, user_id: int):
        return self.api.me_favorite_users_unfollow(user_id)["status"]

    @handle_auth_validation
    def me_following_works(self):
        return self.api.me_following_works()
