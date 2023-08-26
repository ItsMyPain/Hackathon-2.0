from dotenv import load_dotenv
from flask import Flask, render_template

from forms import MainForm
from utils import translate, update_iamtoken

load_dotenv()
app = Flask("elf")

app.config.from_pyfile("config.py")
with app.app_context():
    update_iamtoken()


@app.get("/")
def main_get():
    update_iamtoken()
    form = MainForm()
    return render_template("main.html", form=form)


@app.post("/")
def main_post():
    form = MainForm()
    data = ''
    print(form.data)
    if form.validate():
        data = translate(form.text.data, 'ru', 'en')
        data = translate(data, 'en', 'ru')

    return render_template("main.html", form=form, data=data)


if __name__ == '__main__':
    app.run(debug=True)
