import json
import os
import sys

from flask import Flask

from pixiv.api import API

app = Flask(__name__)
_, pixiv_account, pixiv_password, token_path, image_saving_dir = sys.argv

api = API(pixiv_account, pixiv_password, token_path, image_saving_dir)


@app.route('/')
def hello_world():
    return 'Hello World!1'


@app.route("/query/image/<image_id>")
def query_image(image_id: str):
    return api.works(illust_id=int(image_id))


@app.route("/download/image/<image_id>")
def download_image(image_id: str):
    response = api.works(illust_id=int(image_id))
    urls = response["response"][0]["image_urls"]
    if "large" in urls.keys():
        url = urls["large"]
    elif "medium" in urls.keys():
        url = urls["medium"]
    else:
        url = urls["small"]

    file_name = f"{image_id}.png"
    # existed
    if os.path.isfile(os.path.join(api.image_saving_dir, file_name)):
        return "TRUE"
    else:
        return "TRUE" if api.download(url=url, name=file_name) else "FALSE"


@app.route("/following/display")
def following_display():
    result = api.me_following(per_page=20)
    all_following = []
    for page in range(result["pagination"]["pages"]):
        all_following = all_following + api.me_following(page=page + 1, per_page=20)["response"]
    return json.dumps(all_following)


@app.route("/following/follow/<user_id>")
def follow_user(user_id: str):
    return api.follow(int(user_id))


@app.route("/following/unfollow/<user_id>")
def unfollow_user(user_id: str):
    return api.unfollow(int(user_id))


@app.route("/following/new")
def me_following_works():
    return json.dumps(api.me_following_works()["response"])


if __name__ == '__main__':
    app.run(host="127.0.0.1", port="5000")
