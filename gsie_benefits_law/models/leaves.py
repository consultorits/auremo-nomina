# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import Warning

class typeLeavesSie(models.Model):
    _name = "type.leaves.sie"
    _inherit = ['mail.thread']

    name = fields.Char("Tipo de ausencia")    
    