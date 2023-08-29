import openai
from flask import Flask, render_template, request
from transformers import pipeline

from forms import MainForm
from utils import translate, update_iamtoken, predict_yandex, summarize, additional_text

app = Flask("elf")

app.config.from_pyfile("config.py")
with app.app_context():
    update_iamtoken(1)
    update_iamtoken(2)
    openai.api_key = app.config["OPENAI_API_KEY"]
    app.app_ctx_globals_class.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

menu = {
    "/about": "О нас",
    "/wiki": "Что такое промпт?",
    "/prompt": "Запромптить",
    "/contacts": "Контакты",
}


@app.get('/')
def main():
    return render_template("main.html", menu=menu, page=request.url_rule)


@app.get("/prompt")
def prompt_get():
    update_iamtoken(1)
    update_iamtoken(2)
    form = MainForm()
    return render_template("prompt.html", form=form, menu=menu, page=request.url_rule)


@app.post("/prompt")
def prompt_post():
    form = MainForm()
    data = ''
    if form.validate():
        print('ЗАПРОС:', form.text.data)
        data = summarize(form.text.data)
        data = additional_text(data)
        print()
        print('После добавления текста:', data)
        data = predict_yandex('', data)
        print()
        print('После яндекса:', data)

    return render_template("prompt.html", form=form, data=data, menu=menu, page=request.url_rule)


@app.get("/about")
def about():
    return render_template("about.html", menu=menu, page=request.url_rule)


@app.get("/wiki")
def wiki():
    return render_template("wiki.html", menu=menu, page=request.url_rule)


@app.get("/contacts")
def contacts():
    return render_template("contacts.html", menu=menu, page=request.url_rule)
