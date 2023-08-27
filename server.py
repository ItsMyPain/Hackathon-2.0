import openai
from flask import Flask, render_template
from transformers import pipeline

from forms import MainForm
from utils import translate, update_iamtoken, predict_yandex

app = Flask("elf")

app.config.from_pyfile("config.py")
with app.app_context():
    update_iamtoken(1)
    update_iamtoken(2)
    openai.api_key = app.config["OPENAI_API_KEY"]
    # app.app_ctx_globals_class.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")


@app.get("/")
def main_get():
    update_iamtoken(1)
    update_iamtoken(2)
    form = MainForm()
    return render_template("main.html", form=form)


@app.post("/")
def main_post():
    form = MainForm()
    data = ''
    if form.validate():
        data = translate(form.text.data, 'ru', 'en')
        data = translate(data, 'en', 'ru')
        data = predict_yandex('', data)

    return render_template("main.html", form=form, data=data)


@app.get('/base')
def base():
    return render_template("main.html")

# if __name__ == '__main__':
#     app.run(debug=True)
