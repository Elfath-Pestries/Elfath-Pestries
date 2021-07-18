from odoo import models, fields


class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    home_delivery = fields.Boolean('POS Home Delivery',default=False)