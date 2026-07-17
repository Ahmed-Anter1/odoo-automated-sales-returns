{
    "name": "Portfolio Automated Sales Returns",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Create stock returns and optional credit notes from sale orders",
    "license": "LGPL-3",
    "depends": ["sale_stock", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_order_views.xml",
        "wizard/sale_return_views.xml"
    ],
    "installable": True,
}
