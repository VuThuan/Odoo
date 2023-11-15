from odoo import api, models, tools, fields, _
from odoo.exceptions import UserError, ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    _description = "Inherit purchase order model"

    def action_rfq_send(self):
        result = super(PurchaseOrder, self).action_rfq_send()

        company_id = self.env['res.company'].search([('name', '=', self.partner_id.name)], limit=1)
        if not company_id:
            raise UserError(_("Company not found for partner %s") % self.partner_id.name)

        origin_name = str('SO-') + self.name
        sale_order_data = {
            'partner_id': self.partner_id.id,
            'origin': origin_name,
            'company_id': company_id.id,
            'client_order_ref': origin_name,
            'purchase_order_id': self.id,
            'name': origin_name,
            'order_line': [(0, 0, {
                'product_id': order_line.product_id.id,
                'product_uom_qty': order_line.product_qty,
                'product_uom': order_line.product_uom.id,
                'price_unit': order_line.price_unit,
                'price_subtotal': order_line.price_subtotal,
                'price_tax': order_line.price_tax,
            }) for order_line in self.order_line]
        }

        sale_order = self.env['sale.order'].sudo().search([('purchase_order_id', '=', self.id)], limit=1)

        if sale_order:
            sale_order.write({'order_line': [(5, 0, 0)]})
            sale_order.write(sale_order_data)
        else:
            self.env['sale.order'].sudo().create(sale_order_data)
        return result

    def button_confirm(self):
        result = super(PurchaseOrder, self).button_confirm()
        sale_order = self.env['sale.order'].sudo().search([('purchase_order_id', '=', self.id)], limit=1)

        if sale_order and sale_order.state != 'sale':
            raise ValidationError('A purchase order cannot be confirmed before the sales order has been confirmed.')

        stock_picking = self.env['stock.picking'].search([('origin', '=', self.name)], limit=1)

        if stock_picking:
            stock_picking.write({'state': 'draft'})

        return result
