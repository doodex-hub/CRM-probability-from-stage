# -*- coding: utf-8 -*-

from odoo import _, api, fields, models



class CrmStage(models.Model):
    _inherit = 'crm.stage'


    probability = fields.Float('Probability', default=0.0)
    show_probability = fields.Boolean(compute='_compute_show_probability', string='Show probability')
    
    def _compute_show_probability(self):
        for stage in self:
            # 20.0: get_param() was removed - read the boolean toggle with get_bool().
            stage.show_probability = self.env['ir.config_parameter'].sudo().get_bool('crm.manual.compute.probability')