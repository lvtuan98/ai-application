import os
import re
import zipfile
import gradio as gr

print('hello', gr.__version__)
import time
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
import random
import copy

import string
alphabet = string.digits + string.ascii_lowercase + string.ascii_uppercase + string.punctuation + ' '  # len(aphabet) = 95
'''alphabet
0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ 
'''

# os.system('nvidia-smi')
os.system('ls')


global_dict = {}
#### for interactive
# stack = []
# state = 0   
font = ImageFont.truetype("ai-worker/pipelines/fonts/arial.ttf", 32)

def skip_fun(i, t, guest_id):
    global_dict[guest_id]['state'] = 0
    # global state
    # state = 0


def exe_undo(i, t, guest_id):

    global_dict[guest_id]['stack'] = []
    global_dict[guest_id]['state'] = 0

    # global stack
    # global state
    # state = 0
    # stack = []
    image = Image.open(f'./gray256.jpg')
    # print('stack', stack)
    return image


def exe_redo(i, t, guest_id):
    # global state 
    # state = 0
    global_dict[guest_id]['state'] = 0

    if len(global_dict[guest_id]['stack']) > 0:
        global_dict[guest_id]['stack'].pop()
    image = Image.open(f'./gray256.jpg')
    draw = ImageDraw.Draw(image)

    for items in global_dict[guest_id]['stack']:
        # print('now', items)
        text_position, t = items
        if len(text_position) == 2:
            x, y = text_position
            text_color = (255, 0, 0)  
            draw.text((x+2, y), t, font=font, fill=text_color)
            r = 4
            leftUpPoint = (x-r, y-r)
            rightDownPoint = (x+r, y+r)
            draw.ellipse((leftUpPoint,rightDownPoint), fill='red')
        elif len(text_position) == 4:
            x0, y0, x1, y1 = text_position
            text_color = (255, 0, 0)  
            draw.text((x0+2, y0), t, font=font, fill=text_color)
            r = 4
            leftUpPoint = (x0-r, y0-r)
            rightDownPoint = (x0+r, y0+r)
            draw.ellipse((leftUpPoint,rightDownPoint), fill='red')
            draw.rectangle((x0,y0,x1,y1), outline=(255, 0, 0) )

    print('stack', global_dict[guest_id]['stack'])
    return image

def get_pixels(i, t, guest_id, evt: gr.SelectData):
    # global state

    # register
    if guest_id == '-1':
        seed = str(int(time.time()))
        global_dict[str(seed)] = {
            'state': 0,
            'stack': []
        }
        guest_id = str(seed)
    else:
        seed = guest_id

    text_position = evt.index

    if global_dict[guest_id]['state'] == 0:
        global_dict[guest_id]['stack'].append(
            (text_position, t)
        )
        print(text_position, global_dict[guest_id]['stack'])
        global_dict[guest_id]['state'] = 1
    else:
        
        (_, t) = global_dict[guest_id]['stack'].pop()
        x, y = _
        global_dict[guest_id]['stack'].append(
            ((x,y,text_position[0],text_position[1]), t)
        )
        global_dict[guest_id]['state'] = 0


    image = Image.open(f'./gray256.jpg')
    draw = ImageDraw.Draw(image)

    for items in global_dict[guest_id]['stack']:
        # print('now', items)
        text_position, t = items
        if len(text_position) == 2:
            x, y = text_position
            text_color = (255, 0, 0)  
            draw.text((x+2, y), t, font=font, fill=text_color)
            r = 4
            leftUpPoint = (x-r, y-r)
            rightDownPoint = (x+r, y+r)
            draw.ellipse((leftUpPoint,rightDownPoint), fill='red')
        elif len(text_position) == 4:
            x0, y0, x1, y1 = text_position
            text_color = (255, 0, 0)  
            draw.text((x0+2, y0), t, font=font, fill=text_color)
            r = 4
            leftUpPoint = (x0-r, y0-r)
            rightDownPoint = (x0+r, y0+r)
            draw.ellipse((leftUpPoint,rightDownPoint), fill='red')
            draw.rectangle((x0,y0,x1,y1), outline=(255, 0, 0) )

    print('stack', global_dict[guest_id]['stack'])

    return image, seed


font_layout = ImageFont.truetype('ai-worker/pipelines/fonts/arial.ttf', 16)

def get_layout_image(ocrs):

    blank = Image.new('RGB', (256,256), (0,0,0))
    draw = ImageDraw.ImageDraw(blank)

    for line in ocrs.split('\n'):
        line = line.strip()

        if len(line) == 0:
            break

        pred = ' '.join(line.split()[:-1])
        box = line.split()[-1]
        l, t, r, b = [int(i)*2 for i in box.split(',')] # the size of canvas is 256x256
        draw.rectangle([(l, t), (r, b)], outline ="red")
        draw.text((l, t), pred, font=font_layout)
    
    return blank

        
with gr.Blocks() as demo:


    # guest_id = random.randint(0,100000000)
    # register


    gr.HTML(
        """
        <div style="text-align: center; max-width: 1600px; margin: 20px auto;">
        <h2 style="font-weight: 900; font-size: 2.3rem; margin: 0rem">
            Document Generation
        </h2>
        </div>
        """)

    with gr.Tab("Text-Editing-in-Document"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt = gr.Textbox(label="Prompt. You can let language model automatically identify keywords, or provide them below", placeholder="A beautiful city skyline stamp of Shanghai")
                location = gr.Textbox(label="Location. Should be list by / (e.g., [1, 2, 3, 4]...)", placeholder="[1, 2, 3, 4]")

                # # many encounter concurrent problem
                # with gr.Accordion("(Optional) Template - Click to paint", open=False):
                #     with gr.Row():
                #         with gr.Column(scale=1):
                #             i = gr.Image(label="Canvas", type='filepath', value=f'./gray256.jpg', height=256, width=256)
                #         with gr.Column(scale=1):
                #             t = gr.Textbox(label="Keyword", value='input_keyword')
                #             redo = gr.Button(value='Redo - Cancel the last keyword') 
                #             undo = gr.Button(value='Undo - Clear the canvas') 
                #             skip_button = gr.Button(value='Skip - Operate the next keyword') 


                radio = gr.Radio(["DiffUTE-with-VAE", "DiffUTE-without-VAE"], label="Choice of models", value="DiffUTE-with-VAE")
                slider_natural = gr.Checkbox(label="Natural image generation", value=False, info="The text position and content info will not be incorporated.")
                slider_step = gr.Slider(minimum=1, maximum=50, value=20, step=1, label="Sampling step", info="The sampling step for TextDiffuser-2. You may decease the step to 4 when using LCM.")
                slider_guidance = gr.Slider(minimum=1, maximum=13, value=7.5, step=0.5, label="Scale of classifier-free guidance", info="The scale of cfg and is set to 7.5 in default. When using LCM, cfg is set to 1.")
                slider_batch = gr.Slider(minimum=1, maximum=6, value=4, step=1, label="Batch size", info="The number of images to be sampled.")
                slider_temperature = gr.Slider(minimum=0.1, maximum=2, value=1.4, step=0.1, label="Temperature", info="Control the diversity of layout planner. Higher value indicates more diversity.")
                # slider_seed = gr.Slider(minimum=1, maximum=10000, label="Seed", randomize=True)
                button = gr.Button("Generate")



                guest_id_box = gr.Textbox(label="guest_id", value=f"-1")
                # i.select(get_pixels,[i,t,guest_id_box],[i,guest_id_box])
                # redo.click(exe_redo, [i,t,guest_id_box],[i])
                # undo.click(exe_undo, [i,t,guest_id_box],[i])
                # skip_button.click(skip_fun, [i,t,guest_id_box])

                            
            with gr.Column(scale=1):
                output = gr.Gallery(label='Generated image')

                with gr.Accordion("Intermediate results", open=False):
                    gr.Markdown("Composed prompt")
                    composed_prompt = gr.Textbox(label='')
                    gr.Markdown("Layout visualization")
                    layout = gr.Image(height=256, width=256)


        # button.click(text_to_image, inputs=[guest_id_box, prompt,keywords,positive_prompt, radio,slider_step,slider_guidance,slider_batch,slider_temperature,slider_natural], outputs=[output, composed_prompt, layout])

    gr.HTML(
        """
        <div style="text-align: justify; max-width: 1100px; margin: 20px auto;">
        <h3 style="font-weight: 450; font-size: 0.8rem; margin: 0rem">
        <b>Version</b>: 1.0
        </h3>
        <h3 style="font-weight: 450; font-size: 0.8rem; margin: 0rem">
        <b>Contact</b>: 
        For help or issues using Document Generation, please contact us.
        </h3>
        <h3 style="font-weight: 450; font-size: 0.8rem; margin: 0rem">
        </h3>
        </div>
        """
    )


demo.launch()
