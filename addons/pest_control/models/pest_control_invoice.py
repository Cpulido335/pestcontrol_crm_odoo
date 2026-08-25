import base64
import mimetypes
import re

import requests

from odoo import fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path


class PestControlInvoice(models.Model):
    _name = "pest.control.invoice"
    _description = "Pest Control Invoice"
    _order = "invoice_date desc, id desc"

    # =========================================================
    # FIELDS
    # =========================================================

    name = fields.Char(
        string="Invoice Number",
        readonly=True,
        copy=False,
    )

    service_record_id = fields.Many2one(
        "pest.control.service.record",
        string="Service Record",
        required=True,
        readonly=True,
    )

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer",
        required=True,
        readonly=True,
    )

    invoice_date = fields.Date(
        string="Invoice Date",
        default=fields.Date.context_today,
        readonly=True,
    )

    amount = fields.Monetary(
        string="Amount",
        readonly=True,
    )

    tax = fields.Monetary(
        string="Tax",
        readonly=True,
    )

    total = fields.Monetary(
        string="Total",
        readonly=True,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        readonly=True,
    )

    pdf_attachment_id = fields.Many2one(
        "ir.attachment",
        string="PDF",
        readonly=True,
    )

    # =========================================================
    # ADVANCED INVOICE TEMPLATE VALUES
    # =========================================================

    def _get_advanced_invoice_values(self, record):
        """
        Build the values used by BOTH:
        - the browser Advanced Invoice
        - the archived PDF
        """

        partner = record.customer_id

        city_state = ", ".join(
            value
            for value in [
                partner.city or "",
                partner.state_id.name if partner.state_id else "",
            ]
            if value
        )

        billing_city_state_zip = " ".join(
            value
            for value in [
                city_state,
                partner.zip or "",
            ]
            if value
        )

        job_selection = record._fields["job_type"].selection

        job_type_label = dict(job_selection).get(
            record.job_type,
            "Pest Control Service",
        )

        invoice = record.invoice_id

        if invoice and invoice.name and invoice.name != "New":
            invoice_number = invoice.name
        elif record.job_number and record.job_number != "New":
            invoice_number = record.job_number
        else:
            invoice_number = f"ADV-{record.id:06d}"

        if invoice and invoice.invoice_date:
            invoice_date = invoice.invoice_date
        else:
            invoice_date = fields.Date.context_today(record)

        invoice_date_str = invoice_date.strftime("%m/%d/%Y")

        if record.scheduled_datetime:
            service_dt = fields.Datetime.context_timestamp(
                record,
                record.scheduled_datetime,
            )
            service_date_str = service_dt.strftime("%m/%d/%Y")
        else:
            service_date_str = "N/A"

        return {
            "o": record,
            "billing_name": partner.name or "",
            "billing_street": partner.street or "",
            "billing_city_state_zip": billing_city_state_zip,
            "billing_country": (
                partner.country_id.name
                if partner.country_id
                else ""
            ),
            "invoice_number": invoice_number,
            "invoice_date_str": invoice_date_str,
            "job_type_label": job_type_label,
            "service_address_str": (
                record.service_address.display_name
                if record.service_address
                else "No Address Provided"
            ),
            "service_date_str": service_date_str,
        }

    # =========================================================
    # INLINE STATIC ASSETS
    # =========================================================

    def _inline_pest_control_assets(self, html):
        """
        Replace /pest_control/static/... URLs with data: URIs.

        Browserless runs in its own Docker container, so it cannot
        read Odoo's /mnt/extra-addons filesystem directly. Inlining
        the SVG/PNG assets keeps the PDF generation completely local
        and makes the rendered HTML self-contained.
        """

        module_path = get_module_path("pest_control")

        if not module_path:
            raise UserError(
                "Could not locate the pest_control module."
            )

        pattern = re.compile(
            r'(?P<quote>["\'])'
            r'(?P<url>/pest_control/static/[^"\']+)'
            r'(?P=quote)'
        )

        replacements = {}

        for match in pattern.finditer(html):
            url = match.group("url")

            if url in replacements:
                continue

            relative_path = url.removeprefix(
                "/pest_control/"
            )

            file_path = (
                __import__("pathlib")
                .Path(module_path)
                .joinpath(relative_path)
                .resolve()
            )

            module_root = (
                __import__("pathlib")
                .Path(module_path)
                .resolve()
            )

            try:
                file_path.relative_to(module_root)
            except ValueError:
                raise UserError(
                    f"Invalid static asset path: {url}"
                )

            if not file_path.is_file():
                raise UserError(
                    f"Invoice asset could not be found: {url}"
                )

            mime_type, _ = mimetypes.guess_type(
                str(file_path)
            )

            if not mime_type:
                mime_type = "application/octet-stream"

            raw_data = file_path.read_bytes()

            encoded = base64.b64encode(
                raw_data
            ).decode("ascii")

            replacements[url] = (
                f"data:{mime_type};base64,{encoded}"
            )

        for url, data_uri in replacements.items():
            html = html.replace(
                url,
                data_uri,
            )

        return html

    # =========================================================
    # GENERATE PDF USING LOCAL BROWSERLESS CONTAINER
    # =========================================================

    def generate_pdf(self):
        """
        Render the existing Advanced Invoice QWeb template,
        send the self-contained HTML to the local Browserless
        container, and save the returned PDF as an Odoo attachment.
        """

        self.ensure_one()

        record = self.service_record_id

        if not record:
            raise UserError("This invoice does not have a Service Record.")

        values = self._get_advanced_invoice_values(record)

        html = self.env["ir.qweb"]._render(
            "pest_control.report_advanced_invoice",
            values,
        )

        if isinstance(html, bytes):
            html = html.decode("utf-8")
        else:
            html = str(html)

        # Browserless is a separate Docker container, so embed
        # our local SVG/PNG assets directly into the HTML.
        html = self._inline_pest_control_assets(
            html
        )

        browserless_url = (
            "http://browserless:3000/pdf"
            "?token=pest-control-pdf"
        )

        payload = {
            "html": html,
            "options": {
                "displayHeaderFooter": False,
                "printBackground": True,
                "preferCSSPageSize": True,
            },
        }

        try:
            response = requests.post(
                browserless_url,
                json=payload,
                headers={
                    "Cache-Control": "no-cache",
                    "Content-Type": "application/json",
                },
                timeout=60,
            )

        except requests.RequestException as exc:
            raise UserError(
                "Could not connect to the local PDF renderer."
                "\n\n"
                f"{exc}"
            )

        if response.status_code != 200:
            error_text = response.text

            if len(error_text) > 4000:
                error_text = error_text[:4000] + "\n..."

            raise UserError(
                "Browserless failed to generate the invoice PDF."
                "\n\n"
                f"HTTP status: {response.status_code}"
                "\n\n"
                f"Response:\n{error_text}"
            )

        pdf_data = response.content

        if not pdf_data:
            raise UserError(
                "Browserless returned an empty PDF."
            )

        if not pdf_data.startswith(b"%PDF"):
            content_type = response.headers.get(
                "Content-Type",
                "unknown",
            )

            raise UserError(
                "Browserless returned data, but it was not a PDF."
                "\n\n"
                f"Content-Type: {content_type}"
            )

        # =====================================================
        # SAVE PDF AS ODOO ATTACHMENT
        # =====================================================

        old_attachment = self.pdf_attachment_id

        attachment = self.env[
            "ir.attachment"
        ].create({
            "name": f"{self.name}.pdf",
            "type": "binary",
            "datas": base64.b64encode(
                pdf_data
            ),
            "mimetype": "application/pdf",
            "res_model": self._name,
            "res_id": self.id,
        })

        self.pdf_attachment_id = (
            attachment.id
        )

        # Delete the previous generated PDF only AFTER the
        # replacement has been created successfully.
        if (
            old_attachment
            and old_attachment != attachment
        ):
            old_attachment.unlink()

        return attachment

    # =========================================================
    # OPEN STORED PDF
    # =========================================================

    def action_view_pdf(self):
        self.ensure_one()

        if not self.pdf_attachment_id:
            raise UserError(
                "No PDF has been generated "
                "for this invoice yet."
            )

        return {
            "type": "ir.actions.act_url",
            "url": (
                f"/web/content/"
                f"{self.pdf_attachment_id.id}"
                f"?download=false"
            ),
            "target": "new",
        }