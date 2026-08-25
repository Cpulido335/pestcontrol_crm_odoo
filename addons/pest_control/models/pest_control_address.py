from odoo import api, fields, models


class PestControlAddress(models.Model):
    _name = "pest.control.address"
    _description = "Service Address"
    _rec_name = "display_name"

    name = fields.Char(
        string="Location Label",
        placeholder="e.g. Main Office, North Warehouse, Unit 4B",
    )
    street = fields.Char(string="Street", required=True)
    street2 = fields.Char(string="Street 2")
    city = fields.Char(string="City")
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        domain="[('country_id.code', '=', 'US')]",
        default=lambda self: self.env["res.country.state"].search(
            [
                ("code", "=", "IA"),
                ("country_id.code", "=", "US"),
            ],
            limit=1,
        ).id,
    )
    zip = fields.Char(string="ZIP")
    notes = fields.Text(string="Access Notes / Directions")

    display_name = fields.Char(
        string="Full Address",
        compute="_compute_display_name",
        store=True,
    )

    @api.depends("name", "street", "city", "state_id")
    def _compute_display_name(self):
        for record in self:
            parts = []
            if record.name:
                parts.append(f"[{record.name}]")
            if record.street:
                parts.append(record.street)
            if record.city:
                parts.append(record.city)
            if record.state_id:
                parts.append(record.state_id.code or record.state_id.name)

            record.display_name = (
                ", ".join(parts) if parts else "Unnamed Location"
            )