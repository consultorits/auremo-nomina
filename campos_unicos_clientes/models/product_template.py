# -*- coding: utf-8 -*-
from odoo import models, fields,api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('name')
    def check_mobile(self):
       for rec in self:
           names = self.env['product.template'].search([('name','=',rec.name),('id','!=',rec.id)])
           references = self.env['product.template'].search([('default_code','=',rec.default_code),('id','!=',rec.id)])
           if names:
            raise ValidationError("El Campo Nombre en el producto debe ser unico")
           if references:
            raise ValidationError("El Campo referencia en el producto debe ser unico")
           