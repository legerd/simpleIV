from flask import Flask,render_template, request
import glob
from flask_paginate import Pagination, get_page_parameter
import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import hashlib
import re
import time

from flask_ngrok import run_with_ngrok


ptn=re.compile(r'Seed: \d+')
def get_pnginfo(path):
    targetImage = Image.open(path)
    text=re.sub(ptn,'',targetImage.text["parameters"])
    return str(text)


#Flaskオブジェクトの生成
app = Flask(__name__)
run_with_ngrok(app)

#「/」へアクセスがあった場合に、"Hello World"の文字列を返す
@app.route("/")
def hello():
    return "Hello World"


#「/index」へアクセスがあった場合に、「index.html」を返す
@app.route("/album")
def album():
    generation_type= request.args.get("type", type=str, default="t2i")
    s_zero=time.time()
    page_prompt = request.args.get("page_prompt", type=int, default=1)
    page= request.args.get("page", type=int, default=1)
    limit = 20
    if generation_type=="t2i":
        img_src_list=glob.glob("/mnt/vol_b/stable-diffusion-webui/outputs/txt2img-images/*.png")
    else:
        img_src_list=glob.glob("/mnt/vol_b/stable-diffusion-webui/outputs/img2img-images/*.png")
    img_src_list=[img_src.replace("/mnt/vol_b/","/static/") for img_src in img_src_list]
    img_src_list=sorted(img_src_list,key=get_img_id_from_path, reverse=True)
    # img_src_list=img_src_list[:400]
    fname_list=[os.path.basename(img_src) for img_src in img_src_list]
    name_list=[fname[17:-4] for fname in fname_list]
    name_id_list=[]
    last_name=""
    name_id=-1
    names_unique=[]
    img_list_per_name_id=[]

    for i,name in enumerate(name_list):
        if last_name!=name:
            name_id+=1
            last_name=name
            img_list_per_name_id.append([])
        name_id_list.append(name_id)
        img_list_per_name_id[name_id].append(img_src_list[i])
    img_list_per_name_id_page=img_list_per_name_id[(page_prompt - 1)*limit: page_prompt*limit]
    img_list_page=[x for row in img_list_per_name_id_page for x in row]
    prompt_info_list_page=[get_pnginfo(img_src.replace("/static/","/mnt/vol_b/")) for img_src in img_list_page]
    last_prompt_hash=""
    prompt_id=-1
    img_list_per_prompt_id_page=[]
    prompts_hash_unique_page=[]
    prompt_thumb_list_page=[]
    prompt_id_list_page=[]
    prompt_infos_unique_page=[]
    for i,prompt_info in enumerate(prompt_info_list_page):
        prompt_hash=hashlib.sha1(prompt_info.encode()).hexdigest()
        if last_prompt_hash!=prompt_hash:
            prompt_id+=1
            prompts_hash_unique_page.append(prompt_hash)
            prompt_infos_unique_page.append(prompt_info)
            prompt_thumb_list_page.append(img_list_page[i])
            last_prompt_hash=prompt_hash
            img_list_per_prompt_id_page.append([])
        prompt_id_list_page.append(prompt_id)
        img_list_per_prompt_id_page[prompt_id].append(img_list_page[i])
    ln_prompt=len(name_id_list)
    message="hello"
    pagination_prompt = Pagination(page_prompt=page_prompt, per_page=limit,page_parameter="page_prompt", total=ln_prompt, css_framework='bootstrap5')
    leng=time.time()-s_zero
    return render_template("album.html",prompt_infos_unique=prompt_infos_unique_page,
        prompt_id_list=prompt_id_list_page,img_list_per_prompt_id=img_list_per_prompt_id_page,
        prompt_thumb_list=prompt_thumb_list_page,
        pagination_prompt=pagination_prompt,prompts_hash_unique=prompts_hash_unique_page,data=leng
    )

@app.route("/history")
def history():
    generation_type= request.args.get("type", type=str, default="t2i")
    s_zero=time.time()
    page= request.args.get("page", type=int, default=1)
    limit = 20
    if generation_type=="t2i":
        img_src_list=glob.glob("/mnt/vol_b/stable-diffusion-webui/outputs/txt2img-images/*.png")
    else:
        img_src_list=("/mnt/vol_b/stable-diffusion-webui/outputs/img2img-images/*.png")
    img_src_list=[img_src.replace("/mnt/vol_b/","/static/") for img_src in img_src_list]
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
