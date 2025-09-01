# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import AccessError, UserError
import logging
log = logging.getLogger(__name__).info

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    higher_validation_id = fields.Many2one('purchase.order.approval.group', string=_("Higher validation"), readonly=True, default=False)
    # next_group = fields.Many2one('purchase.order.approval.group',  string=_("Next Group"), readonly=True, compute="get_next_group")
    next_group = fields.Many2one('purchase.order.approval.group',  string=_("Next Group"), readonly=True)
    division_id = fields.Many2one('hr.department', 'Division &amp; Service', check_company=True)

    def create(self, vals):
        purchase = super(PurchaseOrder, self).create(vals)

        # Appel de la méthode get_first_group juste après la création
        if purchase.division_id:

            purchase.next_group = self.env['purchase.order.approval.group'].search([('division_id','=',purchase.division_id.id)]).get_first_group()
        return purchase

    def button_confirm(self):
        if self.can_user_approve():
            return super().button_confirm()
        else:
            self.ensure_one()
            self.write({'state': 'to approve'})
            approval_groups = self.env['purchase.order.approval.group'].search([('max_amount','!=',False)])
            template_id = self.env.ref('cap_purchase_order_approval_group.notify_higher_group_for_purchase_approval')
            template_id.email_to = self.must_send_mail(self.amount_total).mapped('login')
            self.higher_validation_id = approval_groups.get_max_group(self)

            ctx = {
                'default_model': 'purchase.order',
                'default_res_ids': [self.id],
                'default_use_template': bool(template_id),
                'default_template_id': template_id.id  if template_id else None,
                'default_composition_mode': 'comment',  # ou 'mass_mail' / 'comment'
                'force_email': True,  # pour forcer l’envoi réel au lieu d’un message
            }

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'target': 'new',
                'context': ctx,
            }

    def button_approve(self, force=False):
        if self.can_user_approve():
            self.next_group = self.get_next_group(self.next_group)

            if self.can_user_validate() or not self.next_group:
                return super().button_approve()

            # approval_groups = self.env['purchase.order.approval.group'].search([('max_amount','!=',False)])
            # log('approve 2 %r', approval_groups)
            # if self.higher_validation_id:
            #     if not approval_groups.get_max_group(self) or self.higher_validation_id.max_amount >= approval_groups.get_max_group(self).max_amount:
            #         raise AccessError(_("You can't approve this by yourself, please wait for the manager to approve this."))
            #     else:
            #         self.higher_validation_id = approval_groups.get_max_group(self)
            # else:
            #     self.higher_validation_id = approval_groups.get_max_group(self)

            template_id = self.env.ref('cap_purchase_order_approval_group.notify_higher_group_for_purchase_approval').with_user(1)
            template_id.email_to = self.must_send_mail(self.amount_total).mapped('login')

            ctx = {
                'default_model': 'purchase.order',
                'default_res_ids': [self.id],
                'default_use_template': bool(template_id),
                'default_template_id': template_id.id  if template_id else None,
                'default_composition_mode': 'comment',  # ou 'mass_mail' / 'comment'
                'force_email': True,  # pour forcer l’envoi réel au lieu d’un message
            }

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'target': 'new',
                'context': ctx,
            }

    def can_user_approve(self):
        # user_max_group = self.env['purchase.order.approval.group'].search([('max_amount','!=',False)]).get_max_group(self)
        user_id = self.env.user
        if user_id in self.next_group.user_ids:
            return True
        else:
            return False

    def can_user_validate(self):
        # user_max_group = self.env['purchase.order.approval.group'].search([('max_amount','!=',False)]).get_max_group(self)
        user_max_group = self.next_group
        if(user_max_group):
            # validation si le niveau suivant n'est pas requis : on valide depuis niveau 2 si montant non dépassé en niveau 3
            if ((user_max_group.max_amount >= self.amount_total and user_max_group.level in ('3','4'))):
                return True
            else:
                return False
        else:
            return False

    def must_send_mail(self, amount):
        return self.next_group.user_ids

    def get_next_group(self, group):
        next_group = False
        for purchase in self:
            next_group = self.env['purchase.order.approval.group'].search([('division_id','=',purchase.division_id.id)]).get_next_group(group)

        return next_group
