from odoo import api, models, tools, fields, _


class SaleOrder(models.Model):
    _inherit = "sale.order"
    _description = "Inherit Sale Order"

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order Company', readonly=True)

    def action_quotation_send(self):
        result = super(SaleOrder, self).action_quotation_send()
        if self.purchase_order_id:
            purchase_order = self.env['purchase.order'].browse(self.purchase_order_id.id)

            if purchase_order:
                purchase_order_vals = {
                    'order_line': [(0, 0, {
                        'product_id': order_line.product_id.id,
                        'product_qty': order_line.product_uom_qty,
                        'product_uom': order_line.product_uom.id,
                        'price_unit': order_line.price_unit,
                        'price_subtotal': order_line.price_subtotal,
                        'price_tax': order_line.price_tax,
                    }) for order_line in self.order_line],
                }
                purchase_order.sudo().write({'order_line': [(5, 0, 0)]})
                purchase_order.sudo().write(purchase_order_vals)

        return result

    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        if self.purchase_order_id:
            purchase_order = self.env['purchase.order'].sudo().browse(self.purchase_order_id.id)
            purchase_order.button_confirm()
        return result
