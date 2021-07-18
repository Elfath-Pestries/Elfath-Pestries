from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime


class PosDeliveryOrder(models.Model):
    _name = "pos.delivery.order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "POS Delivery Order"
    _order = 'id DESC'

    pos_order_id = fields.Many2one('pos.order')
    delivery_state = fields.Selection([('draft', 'Assigned'),
                                        ('in_progress', 'In Progress'),
                                        ('paid', 'Paid & Delivered'),
                                        ('delivered', 'Delivered'),
                                        ('cancel', 'Cancelled'), ],
                                       'Status', readonly=True, copy=False, default='draft',tracking=True)
    name = fields.Char(string='Order No.', required=True, readonly=True, copy=False)
    partner_id = fields.Many2one('res.partner', string='Customer', change_default=True, index=True)

    '''used only for display purpose, showing the inputed value of pos'''
    display_delivery_time = fields.Datetime(string='Delivery Time',default=fields.Datetime.now,tracking=True)

    '''
        this is the actual delivery time which is stored in utc format in db,use this field to access the delivery time
    '''
    delivery_time = fields.Datetime(string='Delivery Time',default=fields.Datetime.now,readonly=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    email = fields.Char(string="Email")
    phone = fields.Char(string="Mobile/Phone")
    delivery_person = fields.Many2one('res.partner', string="Delivery Person",domain="[('is_driver', '=', True)]")
    bank_statement_ids = fields.One2many('pos.payment', 'pos_delivery_order_id', string='Payments', readonly=True)
    lines = fields.One2many('pos.delivery.order.line', 'order_id', string='Order Lines', readonly=True, copy=True)
    session_id = fields.Many2one('pos.session', string='Session',readonly=True)
    order_date = fields.Datetime(string='Order Date', readonly=True, default=fields.Datetime.now)
    order_ref = fields.Char(string="Order Ref.", readonly=True)
    cashier = fields.Many2one('res.users', string="Cashier")
    order_note = fields.Text()
    order_source = fields.Selection([('pos','POS')], string="Source", default="pos")
    payment_status_with_driver = fields.Boolean("Payment Status with driver")
    payment_status = fields.Char('Payment Status')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', help="The warehouse in which user belongs to.")

    @api.model
    def create(self, vals):
        if vals.get('delivery_person'):
            partner = self.env['res.partner'].browse(int(vals.get('delivery_person'))).ids
            driver_warehouse = self.env['stock.warehouse.driver'].search([('driver_id', 'in', partner)], limit=1)
            if driver_warehouse and driver_warehouse.warehouse_id:
                vals['warehouse_id'] = driver_warehouse.warehouse_id.id
        res = super(PosDeliveryOrder,self.with_context(mail_create_nosubscribe=True)).create(vals)
        return res

    def write(self, vals):
        if vals.get('delivery_person'):
            partner = self.env['res.partner'].browse(int(vals.get('delivery_person'))).ids
            driver_warehouse = self.env['stock.warehouse.driver'].search([('driver_id', 'in', partner)], limit=1)
            if driver_warehouse and driver_warehouse.warehouse_id:
                vals['warehouse_id'] = driver_warehouse.warehouse_id.id
        res = super(PosDeliveryOrder, self).write(vals)
        return res

    @api.onchange('display_delivery_time')
    def onchange_deliverytime(self):
        self.delivery_time = self.display_delivery_time

    def in_progress_action(self):
        self.write({'delivery_state' :'in_progress'})

    def delivered_action(self):
        self.write({'delivery_state': 'delivered'})

    def cancel_action(self):
        self.write({'delivery_state': 'cancel'})

    def make_payment_action(self):
        if self.name:
            pos_order = self.env['pos.order'].search([('pos_reference','=',self.name)])
            if not pos_order:
                raise UserError("POS order not found.\n\n Before making payment, you need to validate POS from frontend.")
            elif pos_order:
                if pos_order.payment_ids:
                    if not self.bank_statement_ids:
                        for i in pos_order.payment_ids:
                            if i.name and 'return' not in i.name:
                                i.write({'name': pos_order.name + ': Home Delivery'})
                            elif not i.name:
                                i.write({'name': pos_order.name + ': Home Delivery'})

                        self.write({'bank_statement_ids': [(6, 0, pos_order.payment_ids.ids)],
                                    'delivery_state': 'paid',
                                    'pos_order_id':pos_order.id,
                                    'order_ref':pos_order.name})


class PosDeliveryOrderLine(models.Model):
    _name = "pos.delivery.order.line"
    _description = "POS Delivery Order Line"

    order_id = fields.Many2one('pos.delivery.order', string='Order Ref', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain=[('sale_ok', '=', True)],
                                 change_default=True)
    price_unit = fields.Float(string='Unit Price', digits=0)
    qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1)


class PosPaymentInherit(models.Model):
    _inherit = "pos.payment"

    pos_delivery_order_id = fields.Many2one('pos.delivery.order', string="POS Delivery Order statement", ondelete='cascade')
