from datetime import datetime,date
from flask import Flask, request, render_template, url_for, redirect,session
from flask_sqlalchemy import BaseQuery, SQLAlchemy
import hashlib

from sqlalchemy.sql.elements import Null
app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db 
from models import Usuario,Movil,Viaje
		
@app.route('/')
def inicio():
	if 'dni' in session: return render_template('aviso.html', aviso="Ya estas iniciado en el sistema...", url=url_for('bienvenida'))
	else: return render_template('inicio.html')
	
@app.route('/registrarse', methods = ['GET','POST'])
def registrarse():   
	if request.method == 'POST':
		if not request.form['nombre'] or not request.form['dni'] or not request.form['password']:
			return render_template('aviso.html', error="Los datos ingresados no son correctos...",url=url_for('inicio'))
		else:
			nuevo_usuario = Usuario(Nombre=request.form['nombre'], DNI = request.form['dni'], Clave=hashlib.md5(bytes(request.form['password'],encoding='utf-8')).hexdigest(),Tipo="cli")	   
			db.session.add(nuevo_usuario)
			db.session.commit()
			return render_template('aviso.html', aviso="El usuario se registró exitosamente",url=url_for('bienvenida'))
	return render_template('nuevo_usuario.html')

@app.route('/ingresar', methods = ['GET','POST'])
def ingresar():
	if request.method == 'POST':
		if not request.form['dni'] or not request.form['password']:
			return render_template('aviso.html', error="Por favor ingrese los datos requeridos",url=url_for('bienvenida'))
		else:
			usuario_actual= Usuario.query.filter_by(DNI= request.form['dni']).first()
			if usuario_actual is None:
				return render_template('aviso.html', error="El dni no está registrado", url=url_for('bienvenida'))
			else:
				if usuario_actual.Clave==hashlib.md5(bytes(request.form['password'],encoding='utf-8')).hexdigest():
					session['dni']=usuario_actual.DNI
					session['tipo']=usuario_actual.Tipo
					return redirect(url_for('bienvenida'))
				else:
					return render_template('aviso.html', error="La contraseña no es válida", url=url_for('bienvenida'))
	else:
		return render_template('ingresar.html')
 
@app.route('/bienvenida')
def bienvenida():
	if 'dni' in session: return render_template('bienvenida.html')
	else: return redirect(url_for('inicio'))

@app.route('/solicitar_movil', methods = ['GET','POST'])
def solicitar_movil():   
	if 'dni' in session:
		if request.method == 'POST':
			if not request.form['origen'] or not request.form['destino']:
				return render_template('aviso.html', error="Los datos ingresados no son correctos...", url=url_for('solicitar_movil'))
			else:
				id=Viaje.query.count()+1
				nuevo_viaje = Viaje(IdViaje=id,Origen=request.form['origen'],Destino=request.form['destino'],DniCliente=session['dni'],
					Fecha=datetime.now().replace(microsecond=0))
				db.session.add(nuevo_viaje)
				db.session.commit()
				return render_template('aviso.html', aviso="Pedido registrado con exito",url=url_for('bienvenida'))
		else: return render_template('solicitar_movil.html')
	else: return render_template('aviso.html', error="Los datos ingresados no son correctos...", url=url_for('solicitar_movil'))

@app.route('/consultar_movil', methods = ['GET','POST'])
def consultar_movil():   
	if 'dni' in session:
		viajes=Viaje.query.filter_by(DniCliente=str(session['dni'])).all()
		if viajes:
			viaje=viajes[len(viajes)-1]
			if viaje:
				if viaje.NumMovil:
					if viaje.Importe:
						aviso='No existen solicitudes pendientes'; datos=None
					else: aviso=None; datos=(viaje.NumMovil, viaje.Demora)
				else: aviso='La solicitud todavia no tiene un movil asignado' ;datos=None
			else: aviso='No has solicitado ningun viaje.';datos=None
		return render_template('consultar_movil.html',aviso=aviso,datos=datos)
	else: return render_template('aviso.html', error="Los datos ingresados no son correctos...", url=url_for('consultar_movil'))

@app.route('/asignar_movil', methods = ['GET','POST'])
def asignar_movil():   
	if 'dni' in session:
		if request.method=='POST':
			if request.form["numMovil"] and request.form["idViaje"] and request.form["demora"]:
				movil=request.form["numMovil"];#movil=movil[len(movil)-1]
				viaje=request.form["idViaje"];#viaje=viaje[len(viaje)-1]
				print(movil,viaje)
				movil=Movil.query.filter_by(Numero=movil).first()#Parece que ahora estas lineas funcionan
				viaje=Viaje.query.filter_by(IdViaje=int(viaje)).first()#agregue algunas lieas arriba pero la verdad ni idea de que cambio que ahora funciona
				if movil.Patente and viaje.DniCliente: 
					print(movil,viaje)
					viaje.Demora=int(request.form["demora"])
					movil.Viaje.append(viaje)
					db.session.commit() 
					return render_template('aviso.html',aviso="El movil se ha asignado al viaje exitosamente.",url=url_for("bienvenida"))
				else: return render_template('aviso.html',error="Algo fallo movil {} viaje {}".format((request.form["numMovil"]),request.form["idViaje"]), url=url_for("asignar_movil"))
			else: return render_template('aviso.html',error="Tiene que seleccionar un viaje y un movil.", url=url_for("asignar_movil"))
		else:
			viajes=Viaje.query.filter_by(NumMovil=None).order_by(Viaje.Fecha).all()
			if viajes:
				moviles=Movil.query.all()
				return render_template('asignar_movil.html',viajes=viajes,moviles=moviles)
			else: return render_template('aviso.html', aviso="No queda ningun viaje pendiente",url=url_for("bienvenida"))
	else: return render_template('aviso.html', error="No tiene acceso a esta pagina...",url=url_for("inicio"))

@app.route('/finalizar_viaje', methods=['GET', 'POST'])
def finalizar_viaje():
	if 'dni' in session:
		if request.method == 'POST':
			if request.form['viaje'] and request.form['duracion']:
				viaje = Viaje.query.filter_by(IdViaje=int(request.form['viaje'])).first()
				if viaje:
					viaje.Duracion = int(request.form['duracion'])
					viaje.Importe = 100 + 5 * viaje.Duracion
					if int(viaje.Demora) > 15:
						viaje.Importe -= viaje.Importe*0.1
					db.session.commit()
					return render_template('finalizar_viaje.html', viaje=viaje)
				else: return render_template('aviso.html', error="No se encontro ningun viaje", url=url_for('bienvenida'))
			else: return render_template('aviso.html', error="Debe seleccionar un viaje", url=url_for("finalizar_viaje"))
		else: #Muestra en la pagina todos los viajes sin finalizar para que el operador elija uno
			viajes = Viaje.query.filter_by(Importe=None).all()
			viajes=[viaje for viaje in viajes if viaje.NumMovil!=None]
			print(viajes)
			if viajes: return render_template('finalizar_viaje.html',viajes=viajes)
			else: return render_template('aviso.html', aviso="No queda ningun viaje para finalizar",url=url_for("bienvenida"))
	else: return render_template('aviso.html', error="No tiene acceso a esta pagina...",url=url_for("inico"))

@app.route('/consultar_viajes', methods = ['GET','POST'])
def consultar_viajes():   
	if 'dni' in session:
		if request.method == 'POST':
			if not request.form['numMovil'] or not request.form['fecha']:
				return render_template('aviso.html', error="Los datos ingresados no son correctos...",url=url_for("consultar_viajes"))
			else:
				s=request.form['fecha']
				s=list(map(int,s.split('-')))
				fecha=date(s[0],s[1],s[2])
				viajes=[]
				suma=0
				for viaje in Viaje.query.filter_by(NumMovil=request.form['numMovil']).all(): 
					print(viaje.Fecha.date(),fecha)
					if viaje.Fecha.date()==fecha and viaje.Importe!=None: 
						viajes.append(viaje)
						suma+=viaje.Importe
				if viajes: return render_template('consultar_viajes.html', viajes=viajes,suma=suma)
				else: return render_template('aviso.html', error="No se encontraron viajes para ese movil en esa fecha",url=url_for("consultar_viajes"))
		else:
			moviles=[movil.Numero for movil in Movil.query.all()]
			hoy='{}-{}-{}'.format(datetime.today().year,datetime.today().month,datetime.today().day)
			return render_template('consultar_viajes.html',moviles=moviles,hoy=hoy)
	else: return render_template('aviso.html', error="Los datos ingresados no son correctos...",url=url_for("inicio"))

@app.route("/Cerrarsesion")
def Cerrarsesion():
	if 'dni' in session:
		session.pop('dni')
		session.pop('tipo')
		return redirect(url_for('inicio'))
	else:
		return render_template("Aviso.html", error="No se inicio sesión.")

if __name__ == '__main__':
	db.create_all()
	app.run(debug = True,port=8000)	