# -*- coding: utf-8 -*-

from odoo import models, fields, api

import logging
_logger = logging.getLogger(__name__)

class detalle_sale_vehiculo(models.Model):
  #  _name = 'detalle_sale_vehiculo'
    _inherit = 'sale.order'
    
    vehiculos = fields.Many2many('gestion_vehiculos.gestion_vehiculos')
    
    def _prepare_invoice(self):
      invoice_vals = super(detalle_sale_vehiculo, self)._prepare_invoice()
      invoice_vals['vehiculos'] = [(6, 0, self.vehiculos.ids)]
      # _logger.error("invoice_vals sale order %s", invoice_vals)
      return invoice_vals