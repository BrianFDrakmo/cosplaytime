from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('prueba.html', title='Prueba Flask', heading='Bienvenidos a Flask!', items=['Item 1', 'Item 2', 'Item 3'])

if __name__ == "__main__":
    app.run(debug=True)