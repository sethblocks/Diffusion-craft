from binascii import Incomplete
from io import BytesIO
import io
import os
import requests
from PIL import Image
import base64
import cv2
import json
import numpy as np

def splitTiles(img):
    rows = img.height / 16
    columns = img.width /16
    out = []
    for column in range(int(rows)):
        for row in range(int(columns)):
            tile = img.crop((row * 16, column * 16, row * 16 + 16, column * 16 + 16))
            
            out.append(tile)
 
    return (out, rows, columns)



def redraw(url, resize):
    img = cv2.imread(url)
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    name = str(os.path.basename(url))
    name =name.removesuffix('.png').replace('_', " ").replace('-', " ")

    imgs = splitTiles(im)

    notencodedImgs, rows, columns = splitTiles(im)



    outputs = []
    total = rows * columns

    for notencoded in notencodedImgs:
        print("loading tile: " + str(notencodedImgs.index(notencoded) + 1) + " / " + str(total))

        tile = cv2.cvtColor(np.asarray(notencoded), cv2.COLOR_RGB2BGR)

        
        retval, bytesimg = cv2.imencode('.png', tile)
        encoded = base64.b64encode(bytesimg).decode('utf-8')
        prompt = {
            "prompt": name + ", video game texture",
            "negative_prompt": "blurry, low quality, bad art, nsfw",
            "steps": 20,
            "init_images": ["data:image/png;base64," + encoded],
            "alwayson_scripts": {
                "controlnet": {
                    "args":[{
                        "input_image": "data:image/png;base64," + encoded,
                        "module": "ip2p",
                        "model": "control_v11p_sd15_ip2p"
                }]
                }
            }

        }


        override = {}
        override["filter_nsfw"] = "true"

        overridePayload = {
            "override_settings": override
        }

        #I couldn't figure it out so I installed an extension

        response = Image.open(io.BytesIO(base64.b64decode(requests.post('http://127.0.0.1:7860/sdapi/v1/img2img', json=prompt).json()['images'][0].split(",", 1)[0])))
        outputs.append(response)
        response.show()

    final = Image.new("RGBA", (int(columns * 16 * resize), int(rows * resize * 16)), "#FFFFFF")
    for row in range(int(rows)):
        for column in range(int(columns)):
            tile = outputs.pop(0)
            tile =tile.resize((16 *resize, 16 * resize))
            final.paste(tile, (column * 16 * resize, row * 16 * resize))


    print("Finished: " + name + " Path:" + url)

    return final

def findall(pathstr):
    for item in os.listdir(pathstr):
        if os.path.isfile(pathstr + "\\" +item):
            if item.endswith(".png"):
                pngs.append(pathstr+ "\\" +item)
        else:
            findall(pathstr +"\\" +item)


pngs = []
try:
    lines = open("incomplete.txt", "r").readlines()
    for l in lines:
        pngs.append(l.removesuffix("\n"))
except:
    findall("C:\\Users\\Seth2\\Desktop\\AIcraft\\bedrock-samples\\resource_pack\\textures\\blocks")


print(pngs[0])


#findall("C:\\Users\\Seth2\\Desktop\\AIcraft\\bedrock-samples\\resource_pack\\textures\\blocks")
try:
    for path in pngs:
        redrawn = redraw(path.removesuffix("\n"), 4)
        if redrawn != Image.new("RGBA", (16 *4, 16*4), "#000000"):
            pngs.remove(path)
            redrawn.save(path.removesuffix("\n"))
except KeyboardInterrupt:
    outfile = open("incomplete.txt", "w+")
    outfile.truncate(0)
    outwrite = ""
    for path in pngs:
        outwrite = outwrite + path + "\n"
    outwrite.removesuffix("\n")
    
    outfile.write(outwrite.removesuffix("\n"))
