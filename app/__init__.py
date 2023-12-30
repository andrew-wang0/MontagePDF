from flask import Flask, render_template

from .routes import views

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret'

app.register_blueprint(views)


@app.errorhandler(500)
def error_500(_error):
    return render_template('500.html')
