# -*- coding: utf-8 -*-
#agregar descripcion
from odoo import models, fields, api


class gestion_marcas(models.Model):
    _name = 'gestion_vehiculos.gestion_marcas'
    _rec_name='marcas'

    marcas = fields.Char(string='Marca')
    modelos_ids = fields.One2many('gestion_vehiculos.gestion_modelo', 'marcas_id', string="Modelos")
    

class gestion_modelo(models.Model):
    _name = 'gestion_vehiculos.gestion_modelo'
    _rec_name='modelos'
    
    modelos = fields.Char(string='modelos')
    marcas_id = fields.Many2one('gestion_vehiculos.gestion_marcas',string='Marca')
    
   
class gestion_vehiculos(models.Model):
    _name = 'gestion_vehiculos.gestion_vehiculos'
    _rec_name='placa'
    
    marca = fields.Many2one('gestion_vehiculos.gestion_marcas',string='Marca')
    modelo = fields.Many2one('gestion_vehiculos.gestion_modelo',string='Modelo')
    dateto = fields.Integer(string='Año')
    color = fields.Char(string='Color')
    placa = fields.Char(string='Placa')
    vin = fields.Char(string='Vin')
    
    _sql_constraints = [('placa_uniq', 'unique (placa)', "La placa ya esta registrada!")]
    
