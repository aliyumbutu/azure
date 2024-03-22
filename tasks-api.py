from flask import Flask, request, jsonify
import json
import os
import pymysql

app = Flask(__name__)

# Database connection parameters - update as needed
DB_USER = os.getenv("DB_USER") or "LAMP2"
DB_PSWD = os.getenv("DB_PSWD") or "password!3P@123"
DB_NAME = os.getenv("DB_NAME") or "task_logger"
DB_HOST = os.getenv("DB_HOST") or "cloudnativedb.mysql.database.azure.com"

db = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PSWD,
    database=DB_NAME,
    cursorclass=pymysql.cursors.DictCursor,
)
cursor = db.cursor()

# Create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    try:
        cursor.execute("INSERT INTO tasks (title) VALUES (%s)", title)
        db.commit()
        cursor.execute("SELECT MAX(id) AS id FROM tasks")
        row = cursor.fetchone()
        resp = get_task(row["id"])
        return jsonify(resp[0]), 201
    except Exception as e:
        return str(e), 500

# Get all tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        cursor.execute(
            "SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created FROM tasks"
        )
        return jsonify(cursor.fetchall()), 200
    except Exception as e:
        return str(e), 500

# Get an individual task
@app.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    try:
        cursor.execute(
            "SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created \
										FROM tasks WHERE id=%s", id
        )
        row = cursor.fetchone()
        return (row if row is not None else "", 200 if row is not None else 404)
    except Exception as e:
        return str(e), 404

# Update an existing task
@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.get_json()
    title = data.get('title')
    try:
        cursor.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, id))
        db.commit()
        return jsonify(get_task(id)), 200
    except Exception as e:
        return str(e), 500

# Delete an existing task
@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    try:
        resp = get_task(id)
        if resp[1] == 200:
            cursor.execute("DELETE FROM tasks WHERE id=%s", id)
            db.commit()
            return "", 200
        else:
            return jsonify(resp), resp[1]
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run()
