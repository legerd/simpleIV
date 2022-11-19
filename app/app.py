from flask import Flask,render_template, request
import glob
from flask_paginate import Pagination, get_page_parameter
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import hashlib
import re
import time
# import paramiko
import warnings
from pyngrok import ngrok

# from flask_ngrok import run_with_ngrok


ptn=re.compile(r'Seed: \d+')
def get_pnginfo(path):
    targetImage = Image.open(path)
    text=re.sub(ptn,'',targetImage.text["parameters"])
    return str(text)


#Flaskオブジェクトの生成
app = Flask(__name__)
# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.WarningPolicy())

# try:
#     with warnings.catch_warnings():
#         warnings.simplefilter("ignore")
#     client.connect(
#         hostname="192.168.0.95",
#         port=5000,
#         username="shono",
#         password="shonoworld",
#     )
# except Exception as e:
#     print(f'*** Failed to connect to {payload["host"]}:{payload["port"]}: {e}')
ngrok.set_auth_token("2H7nHFpElYVDRx5r1qSVDAju4Qq_7UpE8bwMWJkwnYvC36CSw")

http_tunnel = ngrok.connect(5000)
tunnels = ngrok.get_tunnels()
print(tunnels)


# thread = threading.Thread(
#     target=reverse_forward_tunnel,
#     args=(
#         int(payload["remote_port"]),
#         local_server,
#         local_server_port,
#         client.get_transport(),
#     ),
#     daemon=True,
# )
# thread.start()

# run_with_ngrok(app)

#「/」へアクセスがあった場合に、"Hello World"の文字列を返す
@app.route("/")
def history():
    generation_type= request.args.get("type", type=str, default="t2i")
    s_zero=time.time()
    page= request.args.get("page", type=int, default=1)
    limit = 20
    if generation_type=="t2i":
        img_src_list=glob.glob("/storage/data/stable-diffusion-webui/outputs/txt2img-images/*.png")
    else:
        img_src_list=("/storage/data/stable-diffusion-webui/outputs/img2img-images/*.png")
    # img_src_list=[img_src.replace("/mnt/vol_b/","/static/") for img_src in img_src_list]
    img_src_list=sorted(img_src_list,key=get_img_id_from_path, reverse=True)
    img_src_list_page=img_src_list[(page - 1)*limit: page*limit]
    ln=len(img_src_list)
    # prompt_info_list_page=[get_pnginfo(img_src.replace("/static/","/mnt/vol_b/")) for img_src in img_src_list_page]
    pagination = Pagination(page=page, per_page=limit,page_parameter="page", total=ln, css_framework='bootstrap5')
    leng=time.time()-s_zero
    return render_template("history.html",
        pagination=pagination,img_src_list=img_src_list_page,data=leng
    )

def get_img_id_from_path(path):
    return int(os.path.basename(path)[:5])
#おまじない
if __name__ == "__main__":
    app.run()
