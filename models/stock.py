from odoo import models, api
from odoo.exceptions import UserError


class StockWarehouseInherit(models.Model):
    _inherit = "stock.warehouse.driver"

    @api.model
    def create(self, vals):
        if vals.get('driver_id'):
            driver_id = vals.get('driver_id')
            driver_wh = self.env['stock.warehouse.driver'].search([('driver_id', 'in', [driver_id])])
            if driver_wh:
                raise UserError(
                    "You cannot add the delivery boy, the delivery boy is already present in warehouse {}".
                    format(driver_wh.warehouse_id.name))
        res = super(StockWarehouseInherit, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('driver_id'):
            driver_id = vals.get('driver_id')
            driver_wh = self.env['stock.warehouse.driver'].search([('driver_id', 'in', [driver_id])])
            if driver_wh:
                raise UserError(
                    "You cannot add the delivery boy, the delivery boy is already present in warehouse {}".
                        format(driver_wh.warehouse_id.name))
        res = super(StockWarehouseInherit, self).write(vals)
        return res
