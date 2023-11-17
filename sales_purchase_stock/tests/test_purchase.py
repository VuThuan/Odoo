from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestPurchase(TransactionCase):

    def setUp(self):
        super(TestPurchase, self).setUp()
        self.partner = self.env['res.partner'].create({'name': 'Test Partner'})
        self.product = self.env['product.product'].create({'name': 'Test Product', 'type': 'product'})
        self.purchase_order = self.env['purchase.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 2,
                'price_unit': 10,
            })],
        })

    def test_action_rfq_send(self):
        self.purchase_order.action_rfq_send()
        sale_order = self.env['sale.order'].search([('purchase_order_id', '=', self.purchase_order.id)])
        self.assertTrue(sale_order, "Sales Order has created")
        self.assertEqual(sale_order.order_line[0].product_qty, self.purchase_order.order_line[
            0].product_qty, 'Product qty in sale order has same in purchase order')

    def test_sale_order_update_total_action_quotation_send(self):
        sale_order = self.env['sale.order'].search([('purchase_order_id', '=', self.purchase_order.id)])
        sale_order.sudo().write({'order_line': [(5, 0, 0)]})
        sale_order.sudo().write({
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 5,
                'price_unit': 10,
            })],
        })

        sale_order.action_quotation_send()
        purchase_order = self.env['purchase.order'].browse(sale_order.purchase_order_id.id)
        self.assertTrue(purchase_order, "Purchase Order exists")

        self.assertEqual(sale_order.order_line[0].price_subtotal, purchase_order.order_line[0].price_subtotal, 'Subtotal in sale order has same purchase order ')
