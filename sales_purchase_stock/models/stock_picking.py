from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = "Inherit Stock Picking"

    def action_assign(self):
        result = super(StockPicking, self).action_assign()

        if self.origin:
            sale_order = self.env['sale.order'].sudo().search([('name', '=', self.origin)], limit=1)
            if sale_order and sale_order.picking_ids.filtered(lambda p: p.state == 'assigned'):
                purchase_order = sale_order.purchase_order_id
                if purchase_order:
                    purchase_order_picking = purchase_order.picking_ids.filtered(lambda p: p.state != ['assigned', 'done'])
                    if purchase_order_picking:
                        purchase_order_picking.write({'state': 'assigned'})

        return result

    def button_validate(self):
        result = super(StockPicking, self).button_validate()

        if self.origin:
            sale_order = self.env['sale.order'].sudo().search([('name', '=', self.origin)], limit=1)
            if sale_order:
                sale_order_picking = sale_order.picking_ids.filtered(lambda p: p.state != ['assigned', 'done'])
                if sale_order_picking:
                    sale_order_picking.write({'state': 'done'})
        return result
