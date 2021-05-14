from flask import Blueprint, render_template
from flask.globals import request
from flask.helpers import flash
from flask_login.utils import login_required, current_user
from . import db
from .models import Todo
from dateutil import parser
from sqlalchemy import func

main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)

@main.route('/todos', methods=['GET', "POST"])
@login_required
def todos():
    if request.method == 'POST':
        data = request.get_json()

        error = None

        if data:
            title = data.get('title')
            description = data.get('description')
            due_date = data.get('due_date')
            position = data.get('position')

            if not title or not description or not due_date:
                error = 'Please fill in all the fields'
            
            if not error:
                todo = Todo(
                    user_id=current_user.id,
                    title=title,
                    description=description,
                    due_date=parser.parse(due_date)
                )
                db.session.add(todo)
                db.session.flush()
                db.session.commit()

                if position:
                    if position == 'last':
                        res = db.session.query(func.min(Todo.position).label('min_id')).one()
                        position = res.min_id if res.min_id is not None else 1
                        todo.position = position
                    else:
                        todo.position = position + 1

                    rows_updated = Todo.query.filter(Todo.position > int(position)).update({
                        'position': Todo.position + 1
                    })
                else:
                    res = db.session.query(func.max(Todo.position).label('max_id')).one()
                    max = res.max_id if res.max_id is not None else 1
                    todo.position = max + 1

                db.session.commit()

                return todo_to_dict(todo)
        else:
            error = 'Bad Data'
        
        return {
            'status': 'error',
            'msg': error
        }
    else:
        res = db.session.query(func.max(Todo.position)).scalar()
        todos = Todo.query.order_by(Todo.position.desc()).filter_by(user_id=current_user.id).all()

        output = []

        for todo in todos:
            output.append(todo_to_dict(todo))
        
        return {'todos': output}


@main.route('/todo/<int:id>', methods=['GET', 'POST'])
@login_required
def todo(id):
    todo = Todo.query.filter_by(id=id, user_id=current_user.id).first()

    if not todo:
        return {
            'status': 'error',
            'msg': 'Todo not found!'
        }
    
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return {
                'status': 'error',
                'msg': 'Bad data!'
            }

        title = data.get('title')
        description = data.get('description')
        due_date = data.get('due_date')
        is_completed = data.get('is_completed')
        position = data.get('position')

        if not title or not description or is_completed is None or not due_date:
            return {
                'status': 'error',
                'msg': 'Fill in the required fields'
            }
        
        todo.title = title
        todo.description = description
        todo.is_completed = is_completed
        todo.due_date = parser.parse(due_date)
        
        if position:
            if position == 'last':
                res = db.session.query(func.min(Todo.position).label('min_id')).one()
                print("Id %s" % res.min_id)
                position = res.min_id if res.min_id is not None else 1
                todo.position = position
            else:
                todo.position = position + 1
                    
            rows_updated = Todo.query.filter(Todo.position > int(position)).update({
                'position': Todo.position + 1
            })
        else:
            res = db.session.query(func.max(Todo.position).label('max_id')).one()
            max = res.max_id if res.max_id is not None else 1
            todo.position = max + 1

        db.session.commit()

        return todo_to_dict(todo)
    else:
        todo_to_dict(todo)


@main.route('/todo/delete/<int:id>', methods=['POST'])
@login_required
def delete_todo(id):
    todo = Todo.query.filter_by(id=id, user_id=current_user.id)

    if not todo.first():
        return {
            'status': 'error',
            'msg': 'Todo not found!'
        }
    
    data = request.get_json()
    msg = {
        'status': 'success',
        'deleted': data
    }

    todo.delete()
    db.session.commit()

    return msg

def todo_to_dict(todo):
    return {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'position': todo.position,
        'due_date': todo.due_date,
        'is_completed': todo.is_completed
    }


