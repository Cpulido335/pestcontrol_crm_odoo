from odoo import api, models, fields
from odoo.exceptions import UserError

#This is the model for the service record
class ServiceRecord(models.Model):
    _name = "pest.control.service.record"
    _description = "Pest Control Service Record"
    _rec_name = "calendar_title"  #Set _rec_name in your Python model to point directly to your calendar_title field. 




    # --- FIELDS ---
    scheduled_datetime = fields.Datetime(
            string="Scheduled Date & Time",
    )


    job_number = fields.Char( #this is kind of like a unique identifier for the job itself 
        string="Job Number",
        readonly=True,
        copy=False,
        default="New",
    )

    
    date = fields.Date( 
        string="Date",
        compute="_compute_date",
        store=True,
    )

  
    customer_id = fields.Many2one( #res.partner for relational database mapping
        "res.partner", 
        string="Customer",
        required=True,
    )


    service_address = fields.Many2one(
        "pest.control.address",
        string="Service Address",
    )

    job_type = fields.Selection( #The type of job the pest control company performs
        [
            ("general_pest", "General Pest Control"),
            ("initial_service", "Initial Pest Service"),
            ("recurring_service", "Recurring Pest Service"),
            ("follow_up", "Follow-Up Service"),
            ("emergency_service", "Emergency Pest Service"),

            ("bats", "Bat Control"),
            ("ants", "Ant Control"),
            ("bed_bugs", "Bed Bug Control"),
            ("cockroaches", "Cockroach Control"),
            ("fleas", "Flea Control"),
            ("spiders", "Spider Control"),
            ("wasps", "Wasp / Hornet Control"),
            ("bees", "Bee Control"),
            ("flies", "Fly Control"),
            ("mosquitoes", "Mosquito Control"),
            ("ticks", "Tick Control"),
            ("boxelder_bugs", "Boxelder Bug Control"),
            ("stink_bugs", "Stink Bug Control"),
            ("earwigs", "Earwig Control"),
            ("silverfish", "Silverfish Control"),
            ("centipedes", "Centipede / Millipede Control"),
            ("crickets", "Cricket Control"),
            ("pantry_pests", "Pantry Pest Control"),

            ("rodent_control", "Rodent Control"),
            ("mice", "Mouse Control"),
            ("rats", "Rat Control"),
            ("vole_control", "Vole Control"),
            ("wildlife", "Wildlife Control"),

            ("termite", "Termite Control"),
            ("termite_inspection", "Termite Inspection"),
            ("termite_treatment", "Termite Treatment"),
            ("termite_baiting", "Termite Baiting"),

            ("bed_bug_inspection", "Bed Bug Inspection"),
            ("pest_inspection", "General Pest Inspection"),
            ("pre_purchase_inspection", "Pre-Purchase Pest Inspection"),

            ("commercial", "Commercial Pest Control"),
            ("residential", "Residential Pest Control"),
            ("restaurant", "Restaurant / Food Service"),
            ("agricultural", "Agricultural Pest Control"),
            ("industrial", "Industrial Pest Control"),

            ("bait_station", "Bait Station Service"),
            ("trap_service", "Trap Service"),
            ("exclusion", "Pest Exclusion"),
            ("sanitation", "Pest Sanitation"),
            ("preventative", "Preventative Pest Treatment"),

            ("other", "Other"),
        ],
        string="Job Type",
        default="general_pest",
        required=True,
    )


    bait_stations = fields.Integer( #He asked for this, I guess its important to know how many bait stations they use
            string="Bait Stations Used",
            default=0,
    )

    small_bait_stations_used = fields.Integer(
        string="Small Bait Stations Used",
        default=0,
        help="Number of small bait stations used for this service.",
    )

    large_bait_stations_used = fields.Integer(
        string="Large Bait Stations Used",
        default=0,
        help="Number of large bait stations used for this service.",
    )

    # --- INVOICE JOB CHECKBOXES / JOB BOOLEANS ---
    job_inside = fields.Boolean(
        string="Inside",
        default=False,
    )

    job_outside = fields.Boolean(
        string="Outside",
        default=False,
    )

    job_wind = fields.Boolean(
        string="Wind",
        default=False,
    )

    job_general_extermination = fields.Boolean(
        string="General Extermination",
        default=False,
    )

    job_roaches = fields.Boolean(
        string="Roaches",
        default=False,
    )

    job_ants = fields.Boolean(
        string="Ants",
        default=False,
    )

    job_rats = fields.Boolean(
        string="Rats",
        default=False,
    )

    job_mice = fields.Boolean(
        string="Mice",
        default=False,
    )

    job_fleas = fields.Boolean(
        string="Fleas",
        default=False,
    )

    job_bats = fields.Boolean(
        string="Bats",
        default=False,
    )

    job_bed_bugs = fields.Boolean(
        string="Bed Bugs",
        default=False,
    )

    job_termite_inspections = fields.Boolean(
        string="Termite Inspections",
        default=False,
    )

    job_other = fields.Boolean(
        string="Other",
        default=False,
    )
    
    extra = fields.Monetary( #TODO: This might need a name change "Extra"
        string="Extra",
        currency_field="currency_id",
        default=0.0,
        help="Right now 'Extra' just means how much money on materials or traps you spent for when you want to foward that expense to the customer"
    )

    price = fields.Monetary( #The price for JUST the service
        string="Price",
        currency_field="currency_id",
        required=True,
        default=0.0,
        help="The price you want to charge the customer for the pest control service, before tax and extra charges."
    )

    tax = fields.Monetary( #Taxation amount 
        string="Tax",
        currency_field="currency_id",
        compute="_compute_tax",
        default=0.0,
        store=True, #If you want the computed values to actually be available in the list view and searchable/sortable, use: store="True"
        help="Tax is calculated automatically at 7 Percent"
    )

    total = fields.Monetary( #The summations of all the costs as of right now its Price + Extra + Tax
        string="Total",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,  #If you want the computed values to actually be available in the list view and searchable/sortable, use: store="True"
        help="Total is the final amount that the customer is gonna pay for everything, tax is included in thte total"
    )

    notes = fields.Text(
        string="Notes",
    )

    reccomendations = fields.Text(
        string="Reccomendations",
    )

    status = fields.Selection(
        [
            ("job_upcoming", "Upcoming"),
            ("not_sent", "Invoice not sent"),
            ("awaiting_payment", "Awaiting Payment"),
            ("paid", "Paid"),
        ],
        string="Status",
        default="not_sent",
        readonly=False,
        group_expand="_group_expand_status", #this is so that upcoming is the first thing you see when you group by status, this might be more prone to break than other things
    )


    # -------------------------------------------------------------------------
    # CHEMICALS / PRODUCTS USED
    # These fields map directly to the treatment-product section of the
    # paper/HTML invoice.  The *_used boolean lets the technician mark the
    # product as used; the remaining fields capture the amount/rate printed
    # next to that product on the invoice.
    # -------------------------------------------------------------------------

    # Liquid products shown with GAL and % on the invoice
    masterline_used = fields.Boolean(string="Masterline Used")
    masterline_gallons = fields.Float(string="Masterline GAL", default=0.0, digits=(16, 2))
    masterline_percent = fields.Float(
        string="Masterline %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record, for example 0.06 for 0.06%.",
    )

    crossfire_used = fields.Boolean(string="Crossfire Used")
    crossfire_gallons = fields.Float(string="Crossfire GAL", default=0.0, digits=(16, 2))
    crossfire_percent = fields.Float(
        string="Crossfire %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    suspend_used = fields.Boolean(string="Suspend / Suspend Poly Used")
    suspend_gallons = fields.Float(string="Suspend / Suspend Poly GAL", default=0.0, digits=(16, 2))
    suspend_percent = fields.Float(
        string="Suspend / Suspend Poly %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    temprid_used = fields.Boolean(string="Temprid Used")
    temprid_gallons = fields.Float(string="Temprid GAL", default=0.0, digits=(16, 2))
    temprid_percent = fields.Float(
        string="Temprid %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    zenprox_alpine_used = fields.Boolean(string="Zenprox / Alpine Used")
    zenprox_alpine_gallons = fields.Float(string="Zenprox / Alpine GAL", default=0.0, digits=(16, 2))
    zenprox_alpine_percent = fields.Float(
        string="Zenprox / Alpine %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    termidor_he_sc_used = fields.Boolean(string="Termidor HE / SC Used")
    termidor_he_sc_gallons = fields.Float(string="Termidor HE / SC GAL", default=0.0, digits=(16, 2))
    termidor_he_sc_percent = fields.Float(
        string="Termidor HE / SC %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    nyguard_igr_used = fields.Boolean(string="NyGuard IGR Used")
    nyguard_igr_gallons = fields.Float(string="NyGuard IGR GAL", default=0.0, digits=(16, 2))
    nyguard_igr_percent = fields.Float(
        string="NyGuard IGR %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    demand_used = fields.Boolean(string="Demand Used")
    demand_gallons = fields.Float(string="Demand GAL", default=0.0, digits=(16, 2))
    demand_percent = fields.Float(
        string="Demand %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    spectre_ps_used = fields.Boolean(string="Spectre PS Used")
    spectre_ps_gallons = fields.Float(string="Spectre PS GAL", default=0.0, digits=(16, 2))
    spectre_ps_percent = fields.Float(
        string="Spectre PS %",
        default=0.0,
        digits=(16, 4),
        help="Enter the percentage as printed on the service record.",
    )

    # Other treatment products and the units shown on the invoice
    gentrol_used = fields.Boolean(string="Gentrol Used")
    gentrol_ml = fields.Float(string="Gentrol ML", default=0.0, digits=(16, 2))

    alpine_d_used = fields.Boolean(string="Alpine D Used")
    alpine_d_amount = fields.Float(
        string="Alpine D Amount",
        default=0.0,
        digits=(16, 2),
        help="The current invoice has an amount line for Alpine D but does not print a unit next to it.",
    )

    resolve_used = fields.Boolean(string="Resolve Used")
    resolve_oz = fields.Float(string="Resolve Oz.", default=0.0, digits=(16, 2))

    fastrac_used = fields.Boolean(string="Fastrac Used")
    fastrac_oz = fields.Float(string="Fastrac Oz.", default=0.0, digits=(16, 2))

    apprehend_used = fields.Boolean(string="Apprehend Used")
    apprehend_oz = fields.Float(string="Apprehend Oz.", default=0.0, digits=(16, 2))

    weatherblox_used = fields.Boolean(string="WeatherBlox Used")
    weatherblox_oz = fields.Float(string="WeatherBlox Oz.", default=0.0, digits=(16, 2))

    optiguard_quantum_used = fields.Boolean(string="Optiguard / Quantum Used")
    optiguard_quantum_oz = fields.Float(string="Optiguard / Quantum Oz.", default=0.0, digits=(16, 2))

    spot_crack_crevice = fields.Char(
        string="Spot / Crack & Crevice",
        help="Free-form entry for spot, crack, and crevice treatment details.",
    )


    currency_id = fields.Many2one( #not 100% certian we need this but it just forces USD
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    calendar_title = fields.Char(
        string="Calendar Title",
        compute="_compute_calendar_title",
    )

    invoice_id = fields.Many2one(
        "pest.control.invoice",
        string="Invoice",
        readonly=True,
        copy=False,
    )



    # --- @API.DEPENDS ACTIONS ---- 
    @api.depends("scheduled_datetime")
    def _compute_date(self):
        for record in self:
            record.date = record.scheduled_datetime.date() if record.scheduled_datetime else False


    @api.depends("price", "extra")
    def _compute_tax(self):
        for record in self:
            record.tax = (record.price + record.extra) * 0.07

    @api.depends("price", "extra", "tax")
    def _compute_total(self):
        for record in self:
            record.total = record.price + record.extra + record.tax

    @api.depends("customer_id.name", "job_type", "service_address.display_name")
    def _compute_calendar_title(self):
        job_type_dict = dict(self._fields["job_type"].selection)

        for record in self:
            name = (
                record.customer_id.name
                if record.customer_id
                else "No Customer Specified"
            )
            job_label = job_type_dict.get(
                record.job_type, "No Job Type Specified"
            )
            addr = (
                record.service_address.display_name
                if record.service_address
                else "No Address Specified"
            )

            record.calendar_title = f"{addr} - {job_label} - {name}"

    @api.model
    def _group_expand_status(self, states, domain): #this is so that upcoming is the first thing you see when you group by status
        return [
            "job_upcoming",
            "not_sent",
            "awaiting_payment",
            "paid",
        ]




    # --- ACTIONS ----
    def action_open_customer(self): #this is different from window actions. window actions are defined in XML, python actions are more crtical
        self.ensure_one()

        if not self.customer_id:
            return False

        return {
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "res_id": self.customer_id.id,
            "view_mode": "form",
            "target": "current",
        }


    def action_generate_invoice(self):
        self.ensure_one()

        if not self.customer_id:
            raise models.UserError("Please select a customer before generating an invoice.")

        service_date_str = (
            self.scheduled_datetime.strftime("%Y-%m-%d")
            if self.scheduled_datetime
            else "N/A"
        )

        job_type_label = dict(
            self._fields["job_type"].selection
        ).get(self.job_type, "Pest Control Service")

        address_str = self.service_address.display_name if self.service_address else "No Address Provided"
        line_description = (
            f"Pest Control Service - {job_type_label}\n"
            f"Service Date: {service_date_str}\n"
            f"Location: {address_str}"
        )

        # Fetch the 7% tax record defined in data/tax_data.xml
        tax_record = self.env.ref("pest_control.tax_7_percent", raise_if_not_found=False)
        tax_ids_command = [(6, 0, [tax_record.id])] if tax_record else []

        invoice_lines = [
            (
                0,
                0,
                {
                    "name": line_description,
                    "quantity": 1.0,
                    "price_unit": self.price,
                    "tax_ids": tax_ids_command,
                },
            )
        ]

        if self.extra and self.extra > 0:
            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "name": "Additional Service / Extra Charges",
                        "quantity": 1.0,
                        "price_unit": self.extra,
                        "tax_ids": tax_ids_command,
                    },
                )
            )

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.customer_id.id,
                "invoice_date": fields.Date.context_today(self),
                "invoice_line_ids": invoice_lines,
            }
        )

        return {
            "name": "Customer Invoice",
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": invoice.id,
            "view_mode": "form",
            "target": "current",
        }


    def generate_advanced_invoice(self):
        """
        Create/reuse the Pest Control invoice,
        generate and archive its PDF,
        then open the Advanced Invoice in the browser.
        """

        self.ensure_one()

        if not self.customer_id:
            raise UserError(
                "Please select a customer before generating "
                "an advanced invoice."
            )

        invoice = self.invoice_id

        invoice_values = {
            "service_record_id": self.id,

            "customer_id": self.customer_id.id,

            "amount": (
                (self.price or 0.0)
                + (self.extra or 0.0)
            ),

            "tax": self.tax or 0.0,

            "total": self.total or 0.0,

            "currency_id": self.currency_id.id,
        }

        # ---------------------------------------------------------
        # Create invoice only once
        # ---------------------------------------------------------

        if not invoice:

            invoice_number = self.env[
                "ir.sequence"
            ].next_by_code(
                "pest.control.invoice"
            )

            if not invoice_number:
                raise UserError(
                    "The Pest Control invoice sequence "
                    "could not generate an invoice number."
                )

            invoice_values.update({
                "name": invoice_number,

                "invoice_date": fields.Date.context_today(self),
            })

            invoice = self.env[
                "pest.control.invoice"
            ].create(
                invoice_values
            )

            self.invoice_id = invoice

        else:

            # Keep amount/customer information synchronized,
            # but DO NOT issue another invoice number.
            invoice.write(
                invoice_values
            )

        # ---------------------------------------------------------
        # Generate and archive PDF
        # ---------------------------------------------------------

        invoice.generate_pdf()

        # ---------------------------------------------------------
        # Open normal browser invoice like before
        # ---------------------------------------------------------

        return {
            "type": "ir.actions.act_url",

            "url": (
                f"/pest_control/advanced_invoice/{self.id}"
            ),

            "target": "new",
        }