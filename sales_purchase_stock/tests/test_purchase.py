from odoo.tests import TransactionCase


class TestPurchase(TransactionCase):
    def test_action_rfq_send(self):
        self.assertEqual('python'.upper(), 'PYTHON')
