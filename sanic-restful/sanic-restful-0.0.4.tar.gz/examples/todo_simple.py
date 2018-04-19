# from flask import Flask, request
from sanic import Sanic, Blueprint
from sanic_restful import Resource, Api

todos = {}


class TodoSimple(Resource):
    """
    You can try this example as follow:
        $ curl http://localhost:5000/todo1 -d "data=Remember the milk" -X PUT
        $ curl http://localhost:5000/todo1
        {"todo1": "Remember the milk"}
        $ curl http://localhost:5000/todo2 -d "data=Change my breakpads" -X PUT
        $ curl http://localhost:5000/todo2
        {"todo2": "Change my breakpads"}

    Or from python if you have requests :
     >>> from requests import put, get
     >>> put('http://localhost:5000/todo1', data={'data': 'Remember the milk'}).json
     {u'todo1': u'Remember the milk'}
     >>> get('http://localhost:5000/todo1').json
     {u'todo1': u'Remember the milk'}
     >>> put('http://localhost:5000/todo2', data={'data': 'Change my breakpads'}).json
     {u'todo2': u'Change my breakpads'}
     >>> get('http://localhost:5000/todo2').json
     {u'todo2': u'Change my breakpads'}

    """
    async def get(self, request, todo_id):
        return {todo_id: todos[todo_id]}

    async def put(self, request, todo_id):
        todos[todo_id] = request.form.get('data')
        return {todo_id: todos[todo_id]}


app = Sanic(__name__)
bp = Blueprint(__name__, url_prefix='/test')
api = Api(bp)

api.add_resource(TodoSimple, '/<todo_id:int>')
app.register_blueprint(bp)


if __name__ == '__main__':
    app.run(debug=True)
