/** @odoo-module **/
// Tour test BARU untuk project migrasi ini (source 17.0 tidak punya test/tour sama sekali).
// Diadaptasi dari pola resmi Odoo core (addons/crm/static/tests/tours/crm_rainbowman.js) dan
// kerangka migration-tool/templates/test/tour_example.js.template.
//
// Skenario: buat opportunity via kanban quick-create, pindahkan ke stage dengan probability
// dikenal ("QA Tour High", probability=88, dibuat di setUp test Python), verifikasi kolom
// "Probability Revenue" di list view Pipeline menghitung benar (AC-02-01, AC-03-01, AC-03-03).

import { registry } from "@web/core/registry";
import { stepUtils } from "@web_tour/tour_utils";

registry.category("web_tour.tours").add("crm_probability_pipeline_tour", {
    url: "/odoo",
    steps: () => [
        stepUtils.showAppsMenuItem(),
        {
            trigger: ".o_app[data-menu-xmlid='crm.crm_menu_root']",
            content: "Open the CRM app",
            run: "click",
        },
        {
            trigger: ".o-kanban-button-new",
            content: "Create a new opportunity via kanban quick-create",
            run: "click",
        },
        {
            trigger: ".o_field_widget[name=name] input",
            content: "Fill opportunity title",
            run: "edit QA Tour Opportunity",
        },
        {
            trigger: ".o_field_widget[name=expected_revenue] input",
            content: "Fill expected revenue",
            run: "edit 1000",
        },
        {
            trigger: "button.o_kanban_add",
            content: "Save the quick-created opportunity",
            run: "click",
        },
        {
            trigger: ".o_kanban_record:contains('QA Tour Opportunity')",
            content: "Wait for the new card to appear",
        },
        {
            trigger: ".o_kanban_record:contains('QA Tour Opportunity')",
            content: "Drag the opportunity into the 'QA Tour High' stage (probability=88)",
            run: "drag_and_drop (.o_opportunity_kanban .o_kanban_group:has(.o_column_title:contains('QA Tour High')))",
        },
        {
            trigger: ".o_kanban_group:has(.o_column_title:contains('QA Tour High')) .o_kanban_record:contains('QA Tour Opportunity')",
            content: "Wait for the card to land in the target stage column",
        },
        {
            trigger: "button.o_switch_view.o_list",
            content: "Switch to list view",
            run: "click",
        },
        {
            // AC-03-01/AC-03-03: revenue_probability = 1000 * 88 / 100 = 880, displayed in the
            // "Probability Revenue" column this module adds right after "Expected Revenue".
            // AC-02-01: this value can only be 880 if `probability` genuinely followed the stage
            // (88), not left at whatever it was in the "New" stage before the drag.
            trigger: ".o_list_view .o_data_row:contains('QA Tour Opportunity'):contains('880')",
            content: "Assert the row shows the expected Probability Revenue (1000 x 88% = 880)",
        },
    ],
});
