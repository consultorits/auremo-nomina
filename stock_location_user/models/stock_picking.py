# -*- coding: utf-8 -*-
# Part of SysNeo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, _, fields
from odoo.exceptions import ValidationError, UserError

class Picking(models.Model):
    _inherit = "stock.picking"

    def validar_ubicaciones_por_usuario(self):
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                if rec.location_id not in rec.user_id.location_ids:
                    raise UserError("La ubicación %s no es permitida para el usuario %s"%(rec.location_id.display_name, rec.user_id.name))

                for move in rec.move_ids_without_package:
                    if (move.location_id not in rec.user_id.location_ids):
                        raise UserError("La ubicación %s no es permitida para el usuario %s"%(move.location_id.display_name, rec.user_id.name))

    def button_validate(self):
        self.validar_ubicaciones_por_usuario()
        return super(Picking, self).button_validate()
