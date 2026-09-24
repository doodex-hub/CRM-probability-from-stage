from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCrmProbabilityFromStage(TransactionCase):
    """Baseline-equivalence tests — 20.0 must reproduce 19.0 behavior documented in
    doc-dev/migration_19.0_20.0/doc/01_intake/01b_BASELINE_SPEC.md (BSL-NNN) and
    doc-dev/migration_19.0_20.0/doc/05_acceptance/05a_MIGRATION_ACCEPTANCE_CRITERIA.md (AC-NN-NN).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.stage_a = cls.env['crm.stage'].create({'name': 'Test Stage A', 'probability': 20})
        cls.stage_b = cls.env['crm.stage'].create({'name': 'Test Stage B', 'probability': 60})

    def _set_toggle(self, value):
        # 20.0: set_param() was removed; set_bool() is what res.config.settings uses for this field.
        self.env['ir.config_parameter'].sudo().set_bool(
            'crm.manual.compute.probability', value)

    def _make_lead(self, stage, expected_revenue=0.0, partner=False):
        vals = {
            'name': 'Test Opportunity',
            'type': 'opportunity',
            'stage_id': stage.id,
            'expected_revenue': expected_revenue,
        }
        if partner:
            vals['partner_id'] = partner.id
        return self.env['crm.lead'].create(vals)

    # AC-01-01 / BSL-001 — up to 19.0, set_param(key, False) deleted the key entirely. In 20.0
    # set_bool(key, False) keeps the record and stores the string 'False' (native base change),
    # so the raw value must never be read as a truthy string: get_bool() is the contract.
    def test_toggle_saves_config_parameter(self):
        ICP = self.env['ir.config_parameter'].sudo()
        self._set_toggle(True)
        self.assertIs(ICP.get_bool('crm.manual.compute.probability'), True)
        self.assertEqual(ICP.get_str('crm.manual.compute.probability'), 'True')
        self._set_toggle(False)
        self.assertIs(ICP.get_bool('crm.manual.compute.probability'), False)
        self.assertEqual(ICP.get_str('crm.manual.compute.probability'), 'False')

    # AC-01-05 / BSL-001, BSL-004, BSL-009 — the real Settings path (set_values), ON then OFF,
    # must drive both computes. Guards against reading the stored 'False' as a truthy string.
    def test_settings_toggle_roundtrip_drives_computes(self):
        lead = self._make_lead(self.stage_a)
        lead.automated_probability = lead.probability

        self.env['res.config.settings'].create({'crm_manual_compute_probability': True}).execute()
        self.stage_a._compute_show_probability()
        lead._compute_is_automated_probability()
        self.assertTrue(self.stage_a.show_probability)
        self.assertFalse(lead.is_automated_probability)

        self.env['res.config.settings'].create({'crm_manual_compute_probability': False}).execute()
        self.stage_a._compute_show_probability()
        lead._compute_is_automated_probability()
        self.assertFalse(self.stage_a.show_probability)
        self.assertTrue(lead.is_automated_probability)

    # AC-01-02 / AC-01-02b
    def test_show_probability_computed(self):
        self._set_toggle(True)
        self.stage_a._compute_show_probability()
        self.assertTrue(self.stage_a.show_probability)

        self._set_toggle(False)
        self.stage_a._compute_show_probability()
        self.assertFalse(self.stage_a.show_probability)

    # AC-01-03 / BSL-014 — no range validation, must NOT raise
    def test_stage_probability_no_range_validation(self):
        stage_negative = self.env['crm.stage'].create({'name': 'Negative', 'probability': -50})
        self.assertEqual(stage_negative.probability, -50)

        stage_over = self.env['crm.stage'].create({'name': 'Over100', 'probability': 150})
        self.assertEqual(stage_over.probability, 150)

    # AC-02-01 — probability follows stage_id via related field, regardless of toggle
    def test_probability_follows_stage_change(self):
        self._set_toggle(False)
        lead = self._make_lead(self.stage_a)
        self.assertEqual(lead.probability, 20)

        lead.stage_id = self.stage_b
        self.assertEqual(lead.probability, 60)

    # AC-02-02
    def test_is_automated_probability_toggle_off(self):
        self._set_toggle(False)
        lead = self._make_lead(self.stage_a)
        lead.automated_probability = lead.probability
        lead._compute_is_automated_probability()
        self.assertTrue(lead.is_automated_probability)

    # AC-02-03
    def test_is_automated_probability_toggle_on(self):
        self._set_toggle(True)
        lead = self._make_lead(self.stage_a)
        lead.automated_probability = lead.probability
        lead._compute_is_automated_probability()
        self.assertFalse(lead.is_automated_probability)

    # AC-02-04 — toggle ON: was_automated False -> probability follows stage, not PLS
    def test_pls_recompute_toggle_on_follows_stage(self):
        self._set_toggle(True)
        lead = self._make_lead(self.stage_a)
        lead.is_automated_probability = False  # toggle ON forces this (AC-02-03)

        with patch.object(
            type(lead), '_pls_get_naive_bayes_probabilities',
            return_value=({lead.id: 99.0}, {}),
        ):
            lead._compute_probabilities()

        self.assertEqual(lead.automated_probability, 99.0)
        self.assertEqual(lead.probability, self.stage_a.probability)

    # AC-02-05 — toggle OFF: was_automated True -> probability follows PLS result
    def test_pls_recompute_toggle_off_follows_pls(self):
        self._set_toggle(False)
        lead = self._make_lead(self.stage_a)
        lead.active = True
        lead.probability = lead.automated_probability  # equal -> is_automated_probability True
        lead._compute_is_automated_probability()
        self.assertTrue(lead.is_automated_probability)

        with patch.object(
            type(lead), '_pls_get_naive_bayes_probabilities',
            return_value=({lead.id: 42.0}, {}),
        ):
            lead._compute_probabilities()

        self.assertEqual(lead.automated_probability, 42.0)
        self.assertEqual(lead.probability, 42.0)

    # AC-02-06 / BSL-005 — changing the toggle alone does not recompute existing leads
    def test_toggle_change_no_auto_recompute(self):
        self._set_toggle(False)
        lead = self._make_lead(self.stage_a)
        lead.automated_probability = lead.probability
        lead._compute_is_automated_probability()
        self.assertTrue(lead.is_automated_probability)

        self._set_toggle(True)
        # No write on lead.probability/automated_probability -> compute not re-triggered by ORM.
        self.assertTrue(lead.is_automated_probability)

    # AC-03-01
    def test_revenue_probability_calculation(self):
        lead = self._make_lead(self.stage_a, expected_revenue=1000.0)
        self.assertEqual(lead.probability, 20)
        self.assertEqual(lead.revenue_probability, 200.0)

    # AC-03-02 / BSL-015 — partner_id is a dead dependency, recompute is a no-op on value
    def test_revenue_probability_recompute_on_partner_change(self):
        partner = self.env['res.partner'].create({'name': 'Partner X'})
        lead = self._make_lead(self.stage_a, expected_revenue=1000.0)
        before = lead.revenue_probability

        lead.partner_id = partner
        lead._compute_revenue_probability()

        self.assertEqual(lead.revenue_probability, before)
