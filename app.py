import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from functools import wraps

#entorno pythonanywhere
from dotenv import load_dotenv
import os



load_dotenv()


app = Flask(__name__)




app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_CURSORCLASS'] ='DictCursor'
mysql=MySQL(app)


def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get('logueado'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada




@app.route('/')
def entrada():
    entrar_login = url_for('login')
    return render_template('entrada.html', entrar_login=entrar_login)



@app.route('/login', methods=['GET','POST'])
def login():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM portafolio.admin')
    tabla = cur.fetchall()
    tabla = tabla[0]


    if request.method == 'POST':
        usuario = str(request.form['txtusername'].capitalize())
        contraseña = str(request.form['txtpassword'])

        
        if usuario in tabla['usuario'] and contraseña in tabla['password']:
            session['logueado'] = True

            return redirect(url_for('home'))
        else:
            mensaje='El usuario o contraseña ingresada es incorrecta'
            return render_template('login.html', mensaje=mensaje)


    return render_template('login.html')



@app.route('/eliminador', methods=['POST'])
@login_requerido
def eliminador():
    if request.method == 'POST':

        cur = mysql.connection.cursor()

        nombre_habilidad_a_borrar = request.form.get('nombre_habilidad')

        cur.execute(f"DELETE FROM habilidades WHERE titulo_habilidad = '{nombre_habilidad_a_borrar}';")
        mysql.connection.commit()
    return redirect(url_for('home'))






@app.route('/eliminador2', methods=['POST'])
@login_requerido
def eliminador2():
    if request.method == 'POST':

        cur = mysql.connection.cursor()

        hobbie_a_eliminar = request.form.get('acerca_eliminar')

        cur.execute(f"DELETE FROM acerca_de_mi WHERE contenido = '{hobbie_a_eliminar}';")
        mysql.connection.commit()

    return redirect(url_for('home'))




@app.route('/home', methods=['GET','POST'])
@login_requerido
def home():

    cur = mysql.connection.cursor()
    print(cur.execute('''SELECT nombre, email, telefono, mensaje FROM contactos'''))
    contactos = cur.fetchall()
    
    cur.execute('SELECT * FROM habilidades') # habilidades
    habilidades = cur.fetchall()

    perfil = cur.execute('SELECT * FROM acerca_de_mi')
    perfil = cur.fetchall()


    return render_template('home.html', contactos=contactos, habilidades=habilidades, perfil=perfil)


@app.route('/home/insertar', methods=['GET','POST'])
@login_requerido
def insertar():
    cur = mysql.connection.cursor()
    if request.method == 'POST':

        try:
            #peticion de habilidades
            nombre = request.form.get('nombre')
            imagen = request.form.get('imagen')
            contenido = request.form.get('contenido')
        except ValueError:
            print('valores no existen')
        
        try:
            #petición de perfil
            nombre_actividad = request.form.get('nombre_actividad')
            contenido_actividad = request.form.get('contenido_actividad')
        except ValueError:
            print('valores de perfil no existen')

        try:
            #petición de proyecto
            nombre_proyecto = request.form.get('nombre_proyecto')
            Descripcion_proyecto = request.form.get('Descripcion_proyecto')
            Enlace_proyecto = request.form.get('Enlace_proyecto')
        except ValueError:
            print('valores de perfil no existen')



        if nombre and imagen and contenido:
            cur.execute('INSERT INTO portafolio.habilidades (titulo_habilidad,icono_habilidad,habilidad) VALUES (%s,%s,%s)', (nombre,imagen,contenido))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('home'))
        

        if nombre_actividad and contenido_actividad:
            cur.execute('INSERT INTO portafolio.acerca_de_mi (titulo, contenido) VALUES (%s,%s)', (nombre_actividad, contenido_actividad))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('home'))
        
        if nombre_proyecto and Descripcion_proyecto:
            cur.execute('INSERT INTO portafolio.proyectos (nombre_proyecto, descripcion, enlace) VALUES (%s,%s,%s)', (nombre_proyecto, Descripcion_proyecto, Enlace_proyecto))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('home'))


    return render_template('insertar.html')


@app.route('/inicio')
def index(): 

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM habilidades')

    habilidades = cur.fetchall()

    return render_template('index.html', habilidades=habilidades, index=True)

@app.route('/contacto', methods=['GET', 'POST'])
def contacto():

    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nombre = str(request.form['nombre']).capitalize()
        email = str(request.form['email'])
        telefono = str(request.form['telefono'])
        mensaje = str(request.form['mensaje']).capitalize()
        #obtiene los datos del formulario

        if nombre and email and telefono and mensaje:
            cur.execute('INSERT INTO portafolio.contactos (nombre,email,telefono,mensaje) VALUES (%s,%s,%s,%s)',(nombre,email,telefono,mensaje))
            flash('¡Gracias por contactarme! Te responderé pronto.')
            mysql.connection.commit()
            cur.close()
        else:
            print("No se han podido obtener los datos del formulario")

        
        # Aquí puedes agregar la lógica para manejar el formulario, como enviar un correo electrónico o guardar en una base de datos.
        
        return redirect(url_for('contacto'))
    return render_template('contacto.html', contacto=True)

@app.route('/acerca')
def acerca():
    cur = mysql.connection.cursor()
    perfil = cur.execute('SELECT * FROM acerca_de_mi')
    perfil = cur.fetchall()


    return render_template('acerca.html', perfil=perfil,  acerca=True)

@app.route('/proyectos')
def proyectos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM proyectos')
    proyectos = cur.fetchall()
    

    return render_template('proyectos.html', proyectos=True, mis_proyectos=proyectos)

@app.route('/proyecto_productivo')
def proyecto_productivo():  

    texto = [{
        'titulo':'¿De qué trata nuestro proyecto?',
        'contenido':'Este proyecto cuenta con muchas funciones interesantes, entre ellas están llevar un control de el inventario de los productos alimentario del usuario, un apartado de recomendaciones de recetas de cocina y como último un chatbot que te dará recomendaciones de recetas basadas en los ingredientes que tengas a la mano.'
    },
    {
        'titulo':'¿Cúal es su propósito?',
        'contenido':'La razón por la que hacemos este proyecto es para instruir a esas personas que estén interesadas en aprender a cocinar o bien aprender nuevas recetas; esta aplicacion está diseñada tanto para personas recientes en el mundo de la cocina como para decanos experimentados, planeamos que todas las personas puedan tener una experiencia mejor y más eficiente al alcance de su mano.'
    },
    {
        'titulo':'¿Cómo funciona?',
        'contenido':'Estamos iniciando con el proceso de una interfaz gráfica que sea agradable y conprensible para que los usuarios se sientan cómodos, hemos investigado el uso de bases de datos con recetas prediseñadas, y la enlazación de una API de inteligencia artificial para recetas más personalizadas y por último una página donde los usuarios pueden igresar los ingredientes con los que cuentan en el momento.'
    }]
    return render_template('proyecto_productivo.html', texto=texto, proyecto_productivo=True)

@app.route('/calculadora')
def calculadora():    
    return render_template('calculadora.html', calculadora=True)


app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.run(debug=True)
