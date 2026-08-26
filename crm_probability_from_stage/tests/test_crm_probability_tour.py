from odoo.tests import tagged
from odoo.tests.common import HttpCase


@tagged('post_install', '-at_install')
class TestCrmProbabilityPipelineTour(HttpCase):

    def setUp(self):
        super().setUp()
        # Stage with a known, distinctive probability so the tour's assertion (revenue_probability
        # = expected_revenue * probability / 100) is unambiguous regardless of demo data already
        # in the pipeline.
        self.env['crm.stage'].create({'name': 'QA Tour High', 'probability': 88})

    def test_crm_probability_pipeline_tour(self):
        self.start_tour("/odoo", "crm_probability_pipeline_tour", login="admin")


@tagged('post_install', '-at_install')
class TestCrmProbabilitySettingsTour(HttpCase):

    def test_crm_probability_settings_tour(self):
        self.start_tour("/odoo/settings?modules=crm", "crm_probability_settings_tour", login="admin")
        # Server-side assertion (more robust than a DOM read) that the toggle click genuinely
        # persisted, not just that the click event fired.
        param = self.env['ir.config_parameter'].sudo().get_param('crm.manual.compute.probability')
        self.assertEqual(param, 'True')
