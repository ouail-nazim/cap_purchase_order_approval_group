# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
import logging

log = logging.getLogger(__name__).info


class PurchaseOrderApprovals(models.Model):
    _name = "purchase.order.approvals"
    _description = "Approvals purchase orders"

    user_id = fields.Many2one('res.users', 'Approver', required=True)
    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order', required=True)
    group_id = fields.Many2one('purchase.order.approval.group', 'Approval Group', required=True)
    status = fields.Selection(string='Status', required=True, default='to_approve',
                              selection=[('to_approve', 'To Approve'),('approved', 'Approved')])

