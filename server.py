import os

from dotenv import load_dotenv
from flask import Flask, render_template

from forms import MainForm
from utils import translate

load_dotenv()
app = Flask("elf")

app.config.from_pyfile("config.py")
print(app.config)


@app.get("/")
def main_get():
    form = MainForm()
    return render_template("main.html", form=form)


@app.post("/")
def main_post():
    form = MainForm()
    data = ''
    print(form.data)
    if form.validate():
        data = translate(form.text.data, 'ru', 'en')

    return render_template("main.html", form=form, data=data)


if __name__ == '__main__':
    app.run(debug=True)
