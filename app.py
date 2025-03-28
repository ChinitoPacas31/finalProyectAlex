from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'mi_proyecto_final'  

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'task_manager'
}

class Task:
    def __init__(self, task_id, description):
        self.task_id = task_id
        self.description = description
        self.status = "Pending"

class TaskManager:
    def __init__(self):
        self.pending_tasks = []
        self.completed_tasks = []

    def add_task(self, description):
        task_id = len(self.pending_tasks) + 1
        self.pending_tasks.append(Task(task_id, description))

    def complete_task(self, task_id):
        task = next((t for t in self.pending_tasks if t.task_id == task_id), None)
        if task:
            task.status = "Completed"
            self.pending_tasks.remove(task)
            self.completed_tasks.append(task)

    def undo_complete(self):
        if self.completed_tasks:
            task = self.completed_tasks.pop()
            task.status = "Pending"
            self.pending_tasks.append(task)

task_manager = TaskManager()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['user_id'] = user['id']  
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  
        
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            flash('Registro exitoso. Inicia sesión.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('El usuario ya existe', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if "add_task" in request.form:
            task_manager.add_task(request.form.get("task_description"))
        elif "complete_task" in request.form:
            task_manager.complete_task(int(request.form.get("task_id")))
        elif "undo_complete" in request.form:
            task_manager.undo_complete()
        return redirect(url_for('index'))
    
    return render_template('index.html', pending_tasks=task_manager.pending_tasks, completed_tasks=task_manager.completed_tasks, username=session['username'])

if __name__ == '__main__':
    app.run(debug=True)