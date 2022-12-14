# STATIC_DIR="~/workspace/nai/test/"
from flask import Flask,render_template, request,jsonify
import glob
from flask_paginate import Pagination
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import re
import time
import warnings
from numpy import inf
from pyngrok import ngrok
import app.config as config
from urllib.parse import quote
from urllib.parse import unquote


OUTPUTS_DIR=config.OUTPUTS_DIR
STATIC_DIR=config.STATIC_DIR
NGROK_AUTH=config.NGROK_AUTH
# from flask_ngrok import run_with_ngrok

ptn=re.compile(r'Seed: \d+')
def pnginfo_from_path(path):
    targetImage = Image.open(path)
    if "parameters" in targetImage.text.keys():
        text=targetImage.text["parameters"]
        return str(text)
    else:
        return "this image hasn't parametas"
def get_img_id_from_path(path):
    try:
        img_id=int(os.path.basename(path)[:5])
    except:
        img_id=inf
    return img_id

#Flaskオブジェクトの生成
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
ngrok.set_auth_token(NGROK_AUTH)

http_tunnel = ngrok.connect(5000)
tunnels = ngrok.get_tunnels()
print("\n\033[32;1m***NGROK PUBLIC URL***:\033[34m",tunnels[0].public_url,"\033[0m")


# @app.route("/",defaults={'path': quote("stable-diffusion-webui/outputs/txt2img-images", safe='')})
@app.route("/")
@app.route("/list")
def show_list():
    path=quote("stable-diffusion-webui/outputs/txt2img-images", safe='')
    path=request.args.get("path", type=str, default=path)
    path=unquote(path)
    generation_type= request.args.get("type", type=str, default="t2i")
    s_zero=time.time()
    page= request.args.get("page", type=int, default=1)
    limit= request.args.get("limit", type=int, default=100)
    
    # limit = 10
    img_src_list=glob.glob(OUTPUTS_DIR+path+"/*.png")
    img_src_list=[img_src.replace(OUTPUTS_DIR,STATIC_DIR) for img_src in img_src_list]
    img_src_list=sorted(img_src_list,key=get_img_id_from_path, reverse=True)
    img_src_list_page=img_src_list[(page - 1)*limit: page*limit]
    ln=len(img_src_list)
    if page<0 or page>(ln-1)//limit+1:
        page=1
    # prompt_info_list_page=[get_pnginfo(img_src.replace("/static/","/mnt/vol_b/")) for img_src in img_src_list_page]
    pagination = Pagination(page=page, per_page=limit,page_parameter="page",css_framework='',inner_window=1,outer_window=0,link_size=0.7, total=ln,)
    # my_pagination_links=["/"]
    # max_page=
    # if page==1:
    #     my_pagination_links.append("")
    # else:
    #     my_pagination_links.append("/?page="+(page-1))
    # if page==:
    #     my_pagination_links.append("")
    # else:
    #     my_pagination_links.append("/?page="+(page-1))
    leng=time.time()-s_zero
    # meta=jsonify({"meta":"jj"});
    meta=pnginfo_from_path(img_src_list_page[0].replace(STATIC_DIR,OUTPUTS_DIR))
    return render_template("list.html",
        pagination=pagination,img_src_list=img_src_list_page,data=leng,meta=meta,path=path,
    )

@app.route("/pnginfo")
def get_pnginfo():
    path=request.args.get("path", type=str, default="").replace(STATIC_DIR,OUTPUTS_DIR)
    data={"meta":pnginfo_from_path(path)}
    return jsonify(data)

@app.route("/delimg", methods=['POST'])
def del_img():
    path=request.json["path"].replace(STATIC_DIR,OUTPUTS_DIR)
    if os.path.exists(path):
        os.remove(path)
        data={"status":"ok"}
    else:
        data={"status":"not found"}
    return jsonify(data)
# @app.route("/album",defaults={'path':quote("stable-diffusion-webui/outputs/txt2img-images", safe='')})
@app.route("/album")
def show_album():
    # path=unquote(path)
    path=quote("stable-diffusion-webui/outputs/txt2img-images", safe='')
    path=request.args.get("path", type=str, default=path)
    path=unquote(path)
    # path="stable-diffusion-webui/outputs/img2img-images"
    # generation_type= request.args.get("type", type=str, default="t2i")
    limit= request.args.get("limit", type=int, default=100)
    s_zero=time.time()
    page= request.args.get("page", type=int, default=1)
    limit = 12
    # if generation_type=="t2i":
    #     img_src_list=glob.glob(OUTPUTS_DIR+path+"/*.png")
    img_src_list=glob.glob(OUTPUTS_DIR+path+"/*.png")
    img_src_list=[img_src.replace(OUTPUTS_DIR,STATIC_DIR) for img_src in img_src_list]
    img_src_list=sorted(img_src_list,key=get_img_id_from_path, reverse=True)
    img_src_list_page=img_src_list[(page - 1)*limit: page*limit]
    ln=len(img_src_list)
    # prompt_info_list_page=[get_pnginfo(img_src.replace("/static/","/mnt/vol_b/")) for img_src in img_src_list_page]
    pagination = Pagination(page=page, per_page=limit,page_parameter="page", total=ln, css_framework='bootstrap5')
    leng=time.time()-s_zero
    return render_template("history.html",
        pagination=pagination,img_src_list=img_src_list_page,data=leng,path=path,
    )


#おまじない
if __name__ == "__main__":
    app.run()
