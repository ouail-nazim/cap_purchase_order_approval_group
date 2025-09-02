from odoo import api, SUPERUSER_ID
from odoo.exceptions import UserError
import logging
log = logging.getLogger(__name__).info

def test_double_validation_disabled(cr):
    """Test to check if double validation is disabled"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    company_ids = env['res.company'].search([('id','!=',False)])
    if 'two_step' in company_ids.mapped('po_double_validation'):
        raise UserError("You cannot install this module because the double validation for purchase orders by managers is activated")
