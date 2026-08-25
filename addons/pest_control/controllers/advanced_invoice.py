from odoo import http
from odoo.http import request


class PestControlAdvancedInvoiceController(http.Controller):

    @http.route(
        "/pest_control/advanced_invoice/<int:record_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def advanced_invoice(self, record_id, **kwargs):

        record = request.env[
            "pest.control.service.record"
        ].search(
            [("id", "=", record_id)],
            limit=1,
        )

        if not record:
            return request.not_found()

        values = request.env[
            "pest.control.invoice"
        ]._get_advanced_invoice_values(
            record
        )

        return request.render(
            "pest_control.report_advanced_invoice",
            values,
        )