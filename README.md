# Odoo Automated Sales Returns

Installable Odoo 18 addon for creating stock returns from sale orders with an optional full posted-invoice credit note.

## Features

- Return action on confirmed sale orders
- Completed-delivery selection
- Delivered and return quantities
- Quantity validation
- Standard Odoo stock-return workflow
- Optional draft credit note through invoice reversal

Module: `portfolio_sales_returns`  
Dependencies: `sale_stock`, `account`  
License: LGPL-3

The optional credit note reverses the eligible posted invoice in full. Test accounting behavior in a development database before production use.
