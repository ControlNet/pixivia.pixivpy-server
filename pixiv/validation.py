from collections import Callable

from pixivpy3 import PixivError

from pixiv.exception import NotLoginError, TokenError


def auth_validation(block: Callable, self, *args, **kwargs):
    try:
        response = block(self, *args, **kwargs)
    except PixivError as e:
        message = str(e)
        if message == 'Authentication required! Call login() or set_auth() first!':
            raise NotLoginError("Need login in")
        else:
            raise PixivError(message)
    try:
        if response["status"] == "failure":
            if response["errors"]["system"]["message"] == "The access token provided is invalid.":
                raise TokenError("Token invalid")
    except TypeError:
        pass
    return response


def handle_auth_validation(block: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        self = args[0]
        args = args[1:]
        print(kwargs)
        try:
            response = auth_validation(block, self, *args, **kwargs)
        except NotLoginError:
            print("NotLoginError, logging")
            self.login_or_load_token(try_token=True)
            response = auth_validation(block, self, *args, **kwargs)
        except TokenError:
            print("TokenError, logging")
            self.login_or_load_token(try_token=False)
            response = auth_validation(block, self, *args, **kwargs)
        return response

    return wrapper
