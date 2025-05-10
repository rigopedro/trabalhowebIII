from flask import Flask, render_template, redirect
import mysql.connector

app = Flask(__name__)

def connector():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="alakazam_db"
    )

@app.route('/')
def formulario():
    return render_template('formulario.html')

@app.route('/enviar', methods=['POST'])
def enviar():
    nome = request.form['nome']
    email = request.form['email']
    telefone = request.form['telefone']
    idade = request.form['idade']

    conn = connector()
    cursor = conn.cursor()
    sql = "INSERT INTO usuarios (nome, email, telefone, idade) VALUES (%s, %s, %s, %s)"
    val = (nome, email, telefone, idade)
    cursor.execute(sql, val)
    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/')