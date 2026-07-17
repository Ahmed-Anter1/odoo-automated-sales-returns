from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_open_portfolio_return(self):
        self.ensure_one()
        if not self.picking_ids.filtered(lambda record: record.state == "done"):
            raise UserError(_("No completed delivery is available for return."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Sales Return"),
            "res_model": "portfolio.sale.return.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_sale_order_id": self.id},
        }
