/** @odoo-module **/
// Tour test BARU untuk project migrasi ini — verifikasi toggle "Probability from stage" di
// Settings -> CRM benar-benar bisa diklik dan ter-render (AC-01-01, AC-01-04). Persistensi
// nilainya sendiri diverifikasi server-side di companion Python test (bukan lewat DOM assertion
// yang lebih rapuh) setelah `start_tour()` selesai.

import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("crm_probability_settings_tour", {
    url: "/odoo/settings?modules=crm",
    steps: () => [
        {
            trigger: "input[placeholder='Search...']",
            content: "Filter settings to find our toggle",
            run: "edit Probability",
        },
        {
            trigger: ".o_setting_box:has(label:contains('Probability from stage')) input[type='checkbox']",
            content: "Enable 'Probability from stage'",
            run: "click",
        },
        {
            trigger: ".o_form_button_save",
            content: "Save settings",
            run: "click",
        },
        {
            trigger: ".o_form_saved, .o_form_readonly, .o_form_button_save:not(:visible)",
            content: "Wait for the save to actually finish",
        },
    ],
});
