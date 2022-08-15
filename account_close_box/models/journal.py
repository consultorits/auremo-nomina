from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_chash = fields.Boolean(string="Es efectivo")
