from odoo import _, api, fields, models, tools



class CrmLead(models.Model):
    _inherit = 'crm.lead'


    # Computed from the stage (not related): a related field with readonly=False writes every change
    # back to crm.stage (Mark as Lost, manual edit, ...), altering all leads of the stage and failing
    # with an AccessError for users who cannot write on stages.
    probability = fields.Float(
        'Probability', aggregator="avg", copy=False,
        compute='_compute_probability_from_stage', readonly=False, store=True)
    revenue_probability = fields.Float('Probability Revenue', default=0.0, store=True, compute="_compute_revenue_probability")


    def _get_stage_probability(self):
        """Probability a lead takes from its stage; a Won stage always means 100 (core requires it)."""
        self.ensure_one()
        return 100.0 if self.stage_id.is_won else self.stage_id.probability


    @api.depends('stage_id.probability', 'stage_id.is_won')
    def _compute_probability_from_stage(self):
        for lead in self:
            lead.probability = lead._get_stage_probability()


    @api.depends('stage_id', 'probability', 'expected_revenue', 'partner_id')
    def _compute_revenue_probability(self):
        for rec in self:
            rec.revenue_probability = (rec.probability/100)*rec.expected_revenue


    @api.depends('probability', 'automated_probability')
    def _compute_is_automated_probability(self):
        """Base odoo: If probability and automated_probability are equal probability computation
        is considered as automatic, aka probability is sync with automated_probability.
        Doodex enhance: if in parameter is manually compute probability, then the value should following from stage."""
        for lead in self:
            is_manually = self.env['ir.config_parameter'].sudo().get_param('crm.manual.compute.probability', False)
            if not is_manually:
                lead.is_automated_probability = tools.float_compare(lead.probability, lead.automated_probability, 2) == 0
            else:
                lead.is_automated_probability = False


    @api.depends(lambda self: ['stage_id', 'team_id'] + self._pls_get_safe_fields())
    def _compute_probabilities(self):
        lead_probabilities = self._pls_get_naive_bayes_probabilities()
        for lead in self:
            if lead.id in lead_probabilities:
                was_automated = lead.active and lead.is_automated_probability
                lead.automated_probability = lead_probabilities[lead.id]
                if was_automated:
                    lead.probability = lead.automated_probability
                else:
                    lead.probability = lead._get_stage_probability()
    