from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return '''
    <h1>PARADISE</h1>
    <h4>In a higher place, an eternal place of pleasure and joy.</h4>
    '''


if __name__ == '__main__':
    app.run()
