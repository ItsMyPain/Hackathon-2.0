import openai
from flask import Flask, render_template

from forms import MainForm
from utils import translate, update_iamtoken, predict

app = Flask("elf")

app.config.from_pyfile("config.py")
with app.app_context():
    update_iamtoken()
    openai.api_key = app.config["OPENAI_API_KEY"]


@app.get("/")
def main_get():
    update_iamtoken()
    form = MainForm()
    return render_template("main.html", form=form)


@app.post("/")
def main_post():
    form = MainForm()
    data = ''
    if form.validate():
        data = translate(form.text.data, 'ru', 'en')
        data = predict(data)
        data = translate(data, 'en', 'ru')

    return render_template("main.html", form=form, data=data)


@app.get('/base')
def base():
    return render_template("main_page.html")

# if __name__ == '__main__':
#     app.run(debug=True)
