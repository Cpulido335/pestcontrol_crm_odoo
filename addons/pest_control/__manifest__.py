{
    "name": "Pest Control",
    "version": "1.0",
    "category": "Sales",
    "icon": "/pest_control/static/description/icon.svg",
    "depends": [
        "base",
        "contacts",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/tax_data.xml",
        "data/invoice_sequence.xml",
        "views/pest_control_views.xml",
        "report/advanced_invoice_report.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "pest_control/static/src/css/pest_control_backend.css",
        ],
    },
    "installable": True,
    "application": True,
}