from odoo import models, fields, api

class ConfigGsieLeaves(models.Model):
	_name = "gsie.leaves.config"

	#ausencias
	leaves_sie_id = fields.Many2one("type.leaves.sie", "Permiso a cargo de vaciones")
	seleccionado = fields.Boolean("Seleccionado")

	@api.model
	def create(self, vals):
		res = super(ConfigGsieLeaves,self).create(vals)
		if res.seleccionado:
			config = self.env['gsie.leaves.config'].search([('id','!=',res.id)])
			if config:
				for c in config:
					c.write({
						'seleccionado':False
					})
		return res

	def write(self, vals):
		res = super(ConfigGsieLeaves, self).write(vals)
		if self.seleccionado:
			config = self.env['gsie.leaves.config'].search([('id','!=',self.id)])
			if config:
				for c in config:
					c.write({
						'seleccionado':False
					})
		return res
