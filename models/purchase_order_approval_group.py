# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from odoo.exceptions import UserError
import logging
log = logging.getLogger(__name__).info

class PurchaseOrderApprovalGroup(models.Model):
    _name = "purchase.order.approval.group"
    _description = "Approval groups for purchase orders"

    name = fields.Char(_("Name"), required=True)
    # user_ids = fields.Many2many('res.users', string=_("Users"), compute='compute_users_from_department')
    user_ids = fields.Many2many('res.users', string=_("Users"))
    max_amount = fields.Float(_("Max amount"))
    no_limit = fields.Boolean(_("No amount"), default="False")
    division_id = fields.Many2one('hr.department', 'Division & Service', check_company=True)
    level = fields.Selection(
        selection=[
            ('1', 'Valideur 1'),
            ('2', 'Valideur 2'),
            ('3', 'Valideur 3'),
            ('4', 'Valideur 4'),
        ],
        string='Valideur',
        required=True,
        default='1'
    )

    @api.depends('division_id')
    def compute_users_from_department(self):
        for record in self:
            # Exemple : recherche des utilisateurs liés à la division
            user_id = record.division_id.manager_id and record.division_id.manager_id.user_id
            if user_id:
                record.user_ids = [(6, 0, [user_id.id])]
            else:
                record.user_ids = [(6, 0, [])]

    def get_max_group(self, purchase_id):
        user_id = self.env.user
        user_group_id = False
        sorted_groups = self.env['purchase.order.approval.group'].search([]).filtered(lambda x: x.division_id.id == purchase_id.division_id.id
        ).sorted(
            key=lambda x: -int(x.level or 0)
        )

        if not sorted_groups:
            raise UserError('There is no approval group ! Please ask a manager to configure PO approval groups')

        for group_id in sorted_groups:
            if (user_id in group_id.user_ids):
                user_group_id = group_id

        return user_group_id

    def get_higher_groups(self, amount, purchase_id):
        max_group = self.get_max_group(purchase_id)
        sorted_groups = self.env['purchase.order.approval.group'].search([]).sorted(lambda x: (x.no_limit, 1 if x.max_amount else 0))

        if max_group:
            if max_group.no_limit or max_group.max_amount >= amount:
                return False #There is no more group to alert for the caller PO
            else:
                user_max_group_behind = False
                for group_id in sorted_groups:
                    if user_max_group_behind:
                        if group_id.no_limit:
                            return self.search([('no_limit','=',True)])
                        else:
                            return self.search([('max_amount','=',group_id.max_amount)])
                    elif max_group == group_id:
                        user_max_group_behind = True
                return True
        else:
            return self.search([('max_amount','=',sorted_groups[0].max_amount)])

    def get_first_group(self):
        sorted_groups = self.sorted(lambda x: (x.level))
        if not sorted_groups:
            return False
        else:
            return sorted_groups[0]

    def get_next_group(self, group):
        sorted_groups = self.sorted(lambda x: (x.level)).filtered(lambda y: int(y.level)>int(group.level))
        if not sorted_groups:
            return False
        else:
            return sorted_groups[0]
