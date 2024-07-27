import gradio as gr
from PIL import Image
import traceback
import torch
import argparse
from transformers import AutoModel, AutoTokenizer

# Argument parser for device selection
parser = argparse.ArgumentParser(description='Gradio Chatbot Demo')
parser.add_argument('--device', type=str, default='cuda', help='cuda or mps')
args = parser.parse_args()
device = args.device
assert device in ['cuda', 'mps']

# Load model and tokenizer
model_path = 'openbmb/MiniCPM-Llama3-V-2_5'
if 'int4' in model_path and device == 'mps':
    print('Error: running int4 model with bitsandbytes on Mac is not supported right now.')
    exit()

model = AutoModel.from_pretrained(model_path, trust_remote_code=True).to(dtype=torch.float16).to(device=device)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
model.eval()

ERROR_MSG = "Error, please retry"
model_name = 'MiniCPM-Llama3-V 2.5'

# Default parameters
default_params = {
    'sampling': False,
    'stream': False,
    'num_beams': 3,
    'repetition_penalty': 1.2,
    'max_new_tokens': 1024,
    'top_p': 0.8,
    'top_k': 100,
    'temperature': 0.7
}

def chat(img, msgs, ctx, params=None):
    params = params or default_params
    if img is None:
        return "Error, invalid image, please upload a new image"
    try:
        image = img.convert('RGB')
        answer = model.chat(
            image=image,
            msgs=msgs,
            tokenizer=tokenizer,
            **params
        )
        return ''.join(answer) if isinstance(answer, list) else answer
    except Exception as err:
        print(err)
        traceback.print_exc()
        return ERROR_MSG

def upload_img(image, _chatbot, _app_session):
    image = Image.fromarray(image)
    _app_session['sts'] = None
    _app_session['ctx'] = []
    _app_session['img'] = image 
    _chatbot.append(('', 'Image uploaded successfully, you can talk to me now'))
    return _chatbot, _app_session

def respond(_chat_bot, _app_cfg, params_form):
    _question = _chat_bot[-1][0]
    print('<Question>:', _question)
    if _app_cfg.get('ctx', None) is None:
        _chat_bot[-1][1] = 'Please upload an image to start'
        yield (_chat_bot, _app_cfg)
    else:
        _context = _app_cfg['ctx'].copy()
        if _context:
            _context.append({"role": "user", "content": _question})
        else:
            _context = [{"role": "user", "content": _question}]
        
        params = default_params
        gen = chat(_app_cfg['img'], _context, None, params)
        _chat_bot[-1][1] = ""
        for _char in gen:
            _chat_bot[-1][1] += _char
            _context[-1]["content"] += _char
            yield (_chat_bot, _app_cfg)

def request(_question, _chat_bot, _app_cfg):
    _chat_bot.append((_question, None))
    return '', _chat_bot, _app_cfg

def regenerate_button_clicked(_question, _chat_bot, _app_cfg):
    if len(_chat_bot) <= 1:
        _chat_bot.append(('Regenerate', 'No question for regeneration.'))
        return '', _chat_bot, _app_cfg
    elif _chat_bot[-1][0] == 'Regenerate':
        return '', _chat_bot, _app_cfg
    else:
        _question = _chat_bot[-1][0]
        _chat_bot = _chat_bot[:-1]
        _app_cfg['ctx'] = _app_cfg['ctx'][:-2]
    return request(_question, _chat_bot, _app_cfg)

def clear_button_clicked(_question, _chat_bot, _app_cfg, _bt_pic):
    _chat_bot.clear()
    _app_cfg['sts'] = None
    _app_cfg['ctx'] = None
    _app_cfg['img'] = None
    _bt_pic = None
    return '', _chat_bot, _app_cfg, _bt_pic

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1, min_width=300):
            params_form = gr.Radio(
                choices=['Beam Search', 'Sampling'],
                value='Sampling',
                interactive=True,
                label='Decode Type'
            )
            regenerate = gr.Button(
                value='Regenerate',
                interactive=True
            )
            clear = gr.Button(
                value='Clear',
                interactive=True
            )
        with gr.Column(scale=3, min_width=500):
            app_session = gr.State({'sts': None, 'ctx': None, 'img': None})
            bt_pic = gr.Image(label="Upload an image to start")
            chat_bot = gr.Chatbot(label=f"Chat with {model_name}")
            txt_message = gr.Textbox(label="Input text")
            
            clear.click(
                clear_button_clicked,
                [txt_message, chat_bot, app_session, bt_pic],
                [txt_message, chat_bot, app_session, bt_pic],
                queue=False
            )
            txt_message.submit(
                request,
                [txt_message, chat_bot, app_session],
                [txt_message, chat_bot, app_session],
                queue=False
            ).then(
                respond,
                [chat_bot, app_session, params_form],
                [chat_bot, app_session]
            )
            regenerate.click(
                regenerate_button_clicked,
                [txt_message, chat_bot, app_session],
                [txt_message, chat_bot, app_session],
                queue=False
            ).then(
                respond,
                [chat_bot, app_session, params_form],
                [chat_bot, app_session]
            )
            bt_pic.upload(
                lambda: None,
                None,
                chat_bot,
                queue=False
            ).then(
                upload_img,
                inputs=[bt_pic, chat_bot, app_session],
                outputs=[chat_bot, app_session]
            )

demo.queue()
demo.launch()
