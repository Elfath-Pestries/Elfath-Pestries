from odoo import models,fields,api


class PosOrderInherit(models.Model):
    _inherit = "pos.order"

    pos_delivery_order_ref = fields.Many2one('pos.delivery.order',string='Delivery Order Ref',readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('pos_reference'):
            pos_delivery_order = self.env['pos.delivery.order'].search([('name','=',vals.get('pos_reference'))])
            if pos_delivery_order:
                vals['pos_delivery_order_ref'] = pos_delivery_order.id
        res = super(PosOrderInherit, self).create(vals)
        return res
