from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleReturnWizard(models.TransientModel):
    _name = "portfolio.sale.return.wizard"
    _description = "Portfolio Sales Return"

    sale_order_id = fields.Many2one("sale.order", required=True, readonly=True)
    picking_id = fields.Many2one(
        "stock.picking",
        required=True,
        domain="[('sale_id', '=', sale_order_id), ('state', '=', 'done')]",
    )
    line_ids = fields.One2many("portfolio.sale.return.line", "wizard_id")
    create_credit_note = fields.Boolean(default=False)

    @api.onchange("sale_order_id")
    def _onchange_sale_order_id(self):
        for wizard in self:
            deliveries = wizard.sale_order_id.picking_ids.filtered(
                lambda record: record.state == "done"
                and record.picking_type_id.code == "outgoing"
            )
            wizard.picking_id = deliveries.sorted("date_done", reverse=True)[:1]
            wizard.line_ids = [(5, 0, 0)] + [
                (0, 0, {
                    "move_id": move.id,
                    "product_id": move.product_id.id,
                    "delivered_qty": move.quantity,
                    "quantity": 0.0,
                })
                for move in wizard.picking_id.move_ids.filtered(
                    lambda move: move.state == "done" and move.quantity > 0
                )
            ]

    def action_create_return(self):
        self.ensure_one()
        selected = self.line_ids.filtered(lambda line: line.quantity > 0)
        if not selected:
            raise ValidationError(_("Enter a return quantity for at least one product."))
        for line in selected:
            if line.quantity > line.delivered_qty:
                raise ValidationError(
                    _("Return quantity cannot exceed delivered quantity for %s.")
                    % line.product_id.display_name
                )

        ReturnPicking = self.env["stock.return.picking"].with_context(
            active_model="stock.picking",
            active_id=self.picking_id.id,
            active_ids=[self.picking_id.id],
        )
        values = ReturnPicking.default_get(["picking_id", "product_return_moves", "location_id"])
        values["picking_id"] = self.picking_id.id
        return_wizard = ReturnPicking.create(values)

        quantities = {line.move_id.id: line.quantity for line in selected}
        for standard_line in return_wizard.product_return_moves:
            standard_line.quantity = quantities.get(standard_line.move_id.id, 0.0)

        action = return_wizard.action_create_returns()

        if self.create_credit_note:
            invoices = self.sale_order_id.invoice_ids.filtered(
                lambda move: move.state == "posted"
                and move.move_type == "out_invoice"
                and move.payment_state != "reversed"
            )
            if not invoices:
                raise UserError(_("No posted customer invoice is available for reversal."))
            invoices._reverse_moves(
                default_values_list=[
                    {"ref": _("Return for %s") % self.sale_order_id.name}
                    for _invoice in invoices
                ],
                cancel=False,
            )
        return action


class SaleReturnLine(models.TransientModel):
    _name = "portfolio.sale.return.line"
    _description = "Portfolio Sales Return Line"

    wizard_id = fields.Many2one("portfolio.sale.return.wizard", required=True, ondelete="cascade")
    move_id = fields.Many2one("stock.move", required=True, readonly=True)
    product_id = fields.Many2one("product.product", required=True, readonly=True)
    delivered_qty = fields.Float(readonly=True)
    quantity = fields.Float(string="Return Quantity")
