from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
from ...pragmatic_delivery_control_app.controllers.main import WebsiteCustomer
import pytz
import json
import logging

OPG = 5  # Order Per Page

_logger = logging.getLogger(__name__)


class PosHomeDeliveryControl(http.Controller):

    @http.route(['/create/homedelivery'], type='json', auth="none")
    def create_order_home_delivery(self, **post):
        if 'partner_id' in post and 'name' in post and 'product_lst' in post:
            delivery_lst = post.copy()
            del delivery_lst['product_lst']
            pos_delivery_order_srch = request.env['pos.delivery.order'].sudo().search([('name','=',post['name']),
                                                                                       ('delivery_state','!=','cancel')])
            if not pos_delivery_order_srch:
                if delivery_lst['ship_to_diff_addr'] == True:

                    del delivery_lst['ship_to_diff_addr']

                    partner = request.env['res.partner'].sudo().search([('id','=',int(delivery_lst['partner_id']))])
                    current_uid = request.env.context.get('uid')
                    user = request.env['res.users'].sudo().browse(current_uid)

                    if partner and user.company_id:
                        partner_dict={}
                        if 'street' in delivery_lst:
                            partner_dict['street'] = delivery_lst['street'] or ''
                        if 'street2' in delivery_lst:
                            partner_dict['street2'] = delivery_lst['street2'] or ''

                        if 'city' in delivery_lst:
                            partner_dict['city'] = delivery_lst['city'] if delivery_lst['city'] else ''

                        if 'zip' in delivery_lst:
                            partner_dict['zip'] = delivery_lst['zip'] if delivery_lst['zip'] else ''

                        partner_dict['parent_id'] = partner.id
                        partner_dict['type'] = 'delivery'
                        partner_dict['name'] = delivery_lst['customer_name']
                        partner_dict['email'] = delivery_lst['email']
                        res = request.env['res.partner'].sudo().with_context(mail_create_nosubscribe=True,
                                                                             force_company=user.company_id.id).create(partner_dict)
                        delivery_lst['partner_id'] = res.id

                        if 'delivery_time' in post and 'display_delivery_time' in post:
                            delivery_lst['display_delivery_time'] = delivery_lst['display_delivery_time'].replace('T', " ")
                            delivery_lst['delivery_time'] = delivery_lst['delivery_time'].replace('T', " ")

                        del delivery_lst['customer_name']
                        pos_delivery_order = request.env['pos.delivery.order'].sudo().create(delivery_lst)

                        # code for converting delivery time from utc to user timezone
                        if 'delivery_time' in post:
                            delv_time_format = pos_delivery_order.display_delivery_time.strftime(DATETIME_FORMAT)
                            delv_time = datetime.strptime(delv_time_format, DATETIME_FORMAT)
                            tz_name = request.env.context.get('tz') or request.env.user.tz
                            if tz_name:
                                user_dt_tz = pytz.timezone(tz_name).localize(delv_time, is_dst=False).astimezone(
                                    pytz.timezone('UTC')).replace(tzinfo=None)  # UTC = no DST
                                pos_delivery_order.write({'display_delivery_time': user_dt_tz})
                            ########################################################

                        prod_lst = post['product_lst']
                        for i in prod_lst:
                            for j in i:
                                pos_delivery_order.write({
                                    'lines': [(0, 0, {
                                        'product_id': i['id'],
                                        'qty': i['qty'],
                                        'price_unit': i['price_unit'], })]
                                })
                                break
                        return True

                elif not delivery_lst['ship_to_diff_addr'] == True:
                    del delivery_lst['ship_to_diff_addr']
                    partner = request.env['res.partner'].sudo().search([('id','=',int(delivery_lst['partner_id']))])
                    delivery_lst['street'] = partner.street or ''
                    delivery_lst['street2'] = partner.street2 or ''
                    delivery_lst['city'] = partner.city or ''
                    delivery_lst['zip'] = partner.zip or ''
                    if partner.state_id:
                        delivery_lst['state_id'] = partner.state_id.id
                    if partner.country_id:
                        delivery_lst['country_id'] = partner.country_id.id
                    if partner.email:
                        delivery_lst['email'] = partner.email
                    if partner.phone:
                        delivery_lst['phone'] = partner.phone

                    if 'delivery_time' in post and 'display_delivery_time' in post:
                        delivery_lst['display_delivery_time'] = delivery_lst['display_delivery_time'].replace('T', " ")
                        delivery_lst['delivery_time'] = delivery_lst['delivery_time'].replace('T', " ")

                    pos_delivery_order = request.env['pos.delivery.order'].sudo().create(delivery_lst)

                    # code for converting delivery time from utc to user timezone
                    if 'delivery_time' in post:
                        delv_time_format = pos_delivery_order.display_delivery_time.strftime(DATETIME_FORMAT)
                        delv_time = datetime.strptime(delv_time_format, DATETIME_FORMAT)
                        tz_name = request.env.context.get('tz') or request.env.user.tz
                        if tz_name:
                            user_dt_tz = pytz.timezone(tz_name).localize(delv_time,is_dst=False).astimezone(pytz.timezone('UTC')).replace(tzinfo=None)  # UTC = no DST
                            pos_delivery_order.write({'display_delivery_time':user_dt_tz})
                        ########################################################

                    prod_lst = post['product_lst']
                    for i in prod_lst:
                        for j in i:
                            pos_delivery_order.write({
                                'lines': [(0, 0, {
                                    'product_id': i['id'],
                                    'qty':i['qty'],
                                    'price_unit': i['price_unit'], })]
                                })
                            break
                    return True

            else:
                return "already created"
        else:
            return False


class HomeDeliveryControl(http.Controller):

    @http.route('/page/pos-order-view/<order>', type='http', auth='public', website=True, csrf=False)
    def get_pos_order_details(self, order=None, mobilepreview=None):
        do = http.request.env['pos.delivery.order'].sudo()  # pos delivery orders
        pos_delivery_order = do.sudo().search([('name', '=', order)])
        pos = http.request.env['pos.order'].sudo()  # pos delivery orders
        pos_order = pos.sudo().search([('pos_reference', '=', order)],limit=1)
        # order_driver_msg = http.request.env['order.driver.message'].sudo().search(
        #     [('order_id', '=', sale_order.id)])
        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])
        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
        else:
            maps_url = "//maps.google.com/maps/api/js?key=&amp;libraries=places&amp;language=en-AU"
        values = {
            'maps_script_url': maps_url,
            'order': pos_order,
            'longitude': pos_delivery_order.partner_id.partner_longitude,
            'latitude': pos_delivery_order.partner_id.partner_latitude,
            'driver_longitude': pos_delivery_order.warehouse_id.partner_id.partner_longitude,
            'driver_latitude': pos_delivery_order.warehouse_id.partner_id.partner_latitude
        }
        return request.render('home_delivery_odoo_pos_website_mobile_pragtech.pos-order-view', values)

    @http.route('/page/job_list/pos-order-view/<order>', type='http', auth='public', website=True, csrf=False)
    def get_job_list_pos_order_details(self, order=None, mobilepreview=None):
        pos = http.request.env['pos.order'].sudo()
        pos_order = pos.search([('pos_reference','=',order),('pos_delivery_order_ref','=',order)],limit=1)
        # order_driver_msg = http.request.env['order.driver.message'].sudo().search(
        #     [('order_id', '=', sale_order.id)])
        pos_delivery_order = http.request.env['pos.delivery.order'].sudo().search([('name', '=', order)],limit=1)
        api_key = http.request.env['ir.config_parameter'].sudo().search([('key', '=', 'google.api_key_geocode')])
        if len(api_key) == 1:
            maps_url = "//maps.google.com/maps/api/js?key=" + api_key.value + "&amp;libraries=places&amp;language=en-AU"
        else:
            maps_url = "//maps.google.com/maps/api/js?key=&amp;libraries=places&amp;language=en-AU"

        values = {
            'maps_script_url': maps_url,
            'pos_order': pos_order,
            'delivery_order_payment_status': pos_delivery_order.payment_status,
            'longitude': pos_delivery_order.partner_id.partner_longitude,
            'latitude': pos_delivery_order.partner_id.partner_latitude,
            'driver_longitude': pos_delivery_order.warehouse_id.partner_id.partner_longitude,
            'driver_latitude': pos_delivery_order.warehouse_id.partner_id.partner_latitude,
            'driver_mobile': pos_delivery_order.delivery_person.mobile
        }
        return request.render('home_delivery_odoo_pos_website_mobile_pragtech.pos-order-view-driver',values)

    @http.route('/delivered/pos_order', type='http', auth='public', website=True, csrf=False)
    def delivered_pos_order_driver(self, **post):
        order_id = post.get('order_id')
        pos_delivery_order = http.request.env['pos.delivery.order'].sudo().search([('name', '=', order_id)])
        if pos_delivery_order:
            pos_delivery_order.write({'delivery_state':'delivered'})
            return json.dumps({'status': 'true'})

    @http.route('/cancel/posorder', type='http', auth='public', website=True, csrf=False)
    def cancel_pos_order(self, **post):
        order_id = post.get('order_id')
        pos_order = http.request.env['pos.order'].sudo().search([('pos_reference', '=', order_id)], limit=1)
        pos_delivery_order = http.request.env['pos.delivery.order'].sudo().search([('name', '=', order_id)], limit=1)
        if pos_order and pos_delivery_order:
            pos_order.action_pos_order_cancel()
            pos_delivery_order.write({'delivery_state': 'cancel'})
            _logger.info(("Sale order %s has been cancelled from delivery control panel." % (pos_order.name)))
            return json.dumps({'status': 'true'})

    @http.route('/collect-payment-pos', type='http', auth='public', website=True, csrf=False)
    def collect_payment_pos(self, **post):
        if post.get('order_id') and post.get('order_source') == "POS":
            pos_delivery_order = http.request.env['pos.delivery.order'].sudo().search(
                [('name', '=', post.get('order_id'))], limit=1)
            if pos_delivery_order:
                pos_delivery_order.write(
                    {'payment_status_with_driver': True})
        return json.dumps({})

    @http.route('/driver/cancel/pos_order', type='http', auth='public', website=True, csrf=False)
    def driver_cancel_pos_order(self, **post):
        order_id = post.get('order_id')
        pos_delivery_order = request.env['pos.delivery.order'].sudo().search([('name', '=', order_id)],limit=1)
        pos_order = request.env['pos.order'].sudo().search([('pos_reference', '=', order_id)], limit=1)
        if pos_order and pos_delivery_order:
            pos_order.action_pos_order_cancel()
            pos_delivery_order.write({'delivery_state': 'cancel'})
            _logger.info(("Sale order %s has been cancelled from delivery control panel." % (pos_order.name)))
            return json.dumps({'status': 'true'})

    @http.route('/select/payment/pos/status', type='http', auth='public', website=True, csrf=False)
    def customer_payment_status_pos(self, **post):
        order_no = post.get('order_number')
        # pos_order = request.env['pos.order'].sudo().search([('pos_reference','=',order_no)])
        pos_delivery_order = request.env['pos.delivery.order'].sudo().search([('name', '=', order_no)])
        if post.get('selectedValue') == 'cash_on_delivery':
            pos_delivery_order.write({'payment_status': 'Cash On Delivery'})
        elif post.get('selectedValue') == 'prepaid':
            pos_delivery_order.write({'payment_status': 'Prepaid'})
        return json.dumps({})

    @http.route('/paid/pos_order/status', type='http', auth='public', website=True, csrf=False)
    def pos_order_paid_status(self, **post):
        try:
            if post.get('payment_status') == 'PAID':
                order_no = post.get('order_number')
                pos_delivery_order = request.env['pos.delivery.order'].search([('name', '=', order_no)],limit=1)
                pos_order = request.env['pos.order'].search([('pos_reference', '=', order_no)])
                if pos_order and pos_delivery_order:
                    if pos_order.payment_ids:
                        if not pos_delivery_order.bank_statement_ids:
                            for i in pos_order.payment_ids:
                                if i.name and 'return' not in i.name:
                                    i.write({'name': pos_order.name + ': Home Delivery'})
                                elif not i.name:
                                    i.write({'name': pos_order.name + ': Home Delivery'})

                            pos_delivery_order.write({'bank_statement_ids': [(6, 0, pos_order.payment_ids.ids)],
                                                      'delivery_state': 'paid',
                                                      'pos_order_id': pos_order.id,
                                                      'order_ref': pos_order.name})
            return json.dumps({})
        except:
            return False


class WebsiteDeliveryControlAppInherit(WebsiteCustomer):

    @http.route([
        '/page/manage/delivery',
        '/page/manage/delivery/page/<int:page>',
    ], type='http', auth="public", website=True)
    def manage_sale_order_delivery(self, page=0, search='', opg=False, domain=None, **post):
        # res_super = super(WebsiteDeliveryControlAppInherit, self).manage_sale_order_delivery(page,search, opg, domain, **post)
        if domain is None:
            domain = []
        if opg:
            try:
                opg = int(opg)
            except ValueError:
                opg = OPG
            post["ppg"] = opg
        else:
            opg = OPG

        so = request.env['sale.order'].sudo()
        do = request.env['pos.delivery.order'].sudo()  # pos delivery order
        pos = request.env['pos.order'].sudo() # pos order
        usr = request.env['res.users'].sudo().browse(request.uid)

        domain.append(('state', '=', 'sale'))
        so_count = so.search_count(domain)

        url = "/page/manage/delivery"
        # do_count = do.search_count([('state', '=', 'draft')])
        pos_count = pos.search_count([('state', '=', 'paid')])
        total_count = pos_count + so_count
        pager = request.website.pager(url=url, total=total_count, page=page, step=opg, scope=7, url_args=post)
        sale_orders = so.search(domain, limit=opg, offset=pager['offset'], order="id desc")
        pos_orders = pos.search([('state', '=', 'paid'),('pos_delivery_order_ref','!=',False)], limit=opg, offset=pager['offset'], order="id desc")
        # pos_delivery_orders = do.search([('delivery_state', '=', 'draft')], limit=opg, offset=pager['offset'], order="id desc")

        warehouses = http.request.env['stock.warehouse'].sudo().search_read(domain=[], fields=['name'])

        values = {
            'pager': pager,
            'search_count': total_count,  # common for all searchbox
            # 'pos_delivery_orders': pos_delivery_orders,
            'pos_orders': pos_orders,
            'sale_orders': sale_orders,
            'warehouses': warehouses,
            'wh_id': usr.warehouse_id.id
        }

        return request.render("pragmatic_delivery_control_app.manage_sale_order_delivery", values)

    @http.route('/page/job/list', type='http', auth='public', website=True)
    def job_list_website(self, page=0, search='', opg=False, domain=None, **kwargs):
        values = {}
        if request.env.user._is_public():
            return request.render("pragmatic_odoo_delivery_boy.logged_in_template")
        else:
            res_users = request.env['res.users'].search([('id', '=', request.env.user.id)])
            res_partner = request.env['res.partner'].search([('id', '=', res_users.partner_id.id)])
            picking_orders = request.env['picking.order'].search(
                [('state', '=', 'assigned'), ('delivery_boy', '=', res_partner.id), ('state', '!=', 'delivered'),
                 ('state', '!=', 'canceled')])
            pos_delivery_orders = request.env['pos.delivery.order'].search([('delivery_state', 'in', ['draft','in_progress','paid']),
                                                                            ('delivery_person', '=', res_partner.id)
                                                                            ,('delivery_state', 'not in', ['delivered','cancel']),
                                                                            ]).ids
            values = {
                'picking_orders': picking_orders,
            }
            if pos_delivery_orders:
                pos_orders = request.env['pos.order'].search(
                    [('state', '=', 'paid'), ('pos_delivery_order_ref', 'in', pos_delivery_orders)])

                values['pos_orders'] = pos_orders

            return request.render("pragmatic_odoo_delivery_boy.manage_job_list", values)
