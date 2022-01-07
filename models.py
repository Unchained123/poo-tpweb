from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy(app)

class Usuario(db.Model):
	DNI = db.Column(db.String(8), primary_key=True,unique=True)
	Nombre = db.Column(db.String(80), nullable=False)
	Clave = db.Column(db.String(120), nullable=False)    
	Tipo = db.Column(db.String(5), nullable=False)    
	Viaje = db.relationship('Viaje',backref='Usuario',lazy='dynamic')
	
class Movil(db.Model):
	Numero=db.Column(db.Integer,primary_key=True)
	Patente=db.Column(db.String(7),nullable=False)
	Marca=db.Column(db.String(20),nullable=False)
	Viaje=db.relationship('Viaje',backref='Movil',lazy='dynamic')

class Viaje(db.Model):
	IdViaje=db.Column(db.Integer,primary_key=True)
	Origen=db.Column(db.String(50),nullable=False)
	Destino=db.Column(db.String(50),nullable=False)
	Fecha=db.Column(db.DateTime,nullable=True)
	Demora=db.Column(db.Integer,nullable=True)
	Duracion=db.Column(db.Integer,nullable=True)
	Importe=db.Column(db.Float,nullable=True)
	DniCliente=db.Column(db.Integer, db.ForeignKey('usuario.DNI'))
	NumMovil=db.Column(db.Integer,db.ForeignKey('movil.Numero'))
