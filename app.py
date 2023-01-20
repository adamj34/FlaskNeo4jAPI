from flask import Flask
from employees import employees
from departments import departments


app = Flask(__name__)

app.register_blueprint(employees)
app.register_blueprint(departments)


if __name__ == '__main__':
    app.run()