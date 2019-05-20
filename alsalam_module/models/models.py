# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import re

class SalesOrder(models.Model):
    _inherit = 'sale.order'
    _description = 'Sale order customize'

    user_id = fields.Many2one('res.users', string='Cashier', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user)
    x_sale_person = fields.Many2one('res.users', string='Sales Person')
    x_sale_type = fields.Selection([
        ('cr', 'Credit'),
        ('pod', 'Payment On Delivery')], string="Sales Type")

    @api.multi
    @api.onchange('x_sale_type')
    def get_new_ref(self):
        name1 = self.env['ir.sequence'].next_by_code('sales.ordercr')
        name2 = self.env['ir.sequence'].next_by_code('sales.orderpod')
        for record in self:
            if record.x_sale_type == 'cr':
                record.update({
                    'name':  name1
                })
            if record.x_sale_type == 'pod':
                record.update({
                    'name': name2
                })


class SalesLines(models.Model):
    _inherit = 'sale.order.line'
    _description = 'sale line customization'

    x_expected_date = fields.Datetime(string="Expected Date", related='order_id.expected_date')
    x_resevation = fields.One2many('location.detail', 'order_line_id')
    x_available_stock = fields.Float(string='Stock')
    x_displayed_qty = fields.Float(string='Displayed')
    x_damaged_qty = fields.Float(string='Damaged')
    x_reserved_qty = fields.Float(string='Reserved')
    x_remain_qty = fields.Float(string='Available')
    x_warehouse = fields.Char(string='Warehouse')

    @api.onchange('product_id')
    def last_ordered(self):
        for order in self:
            list2 = []

            for ids in order.order_id:
                stock = order.env['stock.quant'].search([('product_id', '=', order.product_id.id)])
                for move in stock:
                    lines2 = (0, 0, {
                        'warehouse': move.location_id.location_id.name,
                        'available_stock': move.quantity,
                        'displayed_qty': '',
                        'damaged_qty': '',
                        'reserved_qty': move.reserved_quantity,
                        'remain_qty': move.quantity - move.reserved_quantity
                    })
                    list2.append(lines2)
                    order.update({'x_resevation': list2})
                    # print(move.product_uom_qty)
                    # print(move.reference)
                    # print(move.move_id.sale_line_id.order_partner_id.name)
                    # print(move.date)

class Warehouse(models.Model):
    _name = 'location.detail'
    _description = 'Resevation Summary'

    available_stock = fields.Float(string='Stock')
    displayed_qty = fields.Float(string='Displayed')
    damaged_qty = fields.Float(string='Damaged')
    reserved_qty = fields.Float(string='Reserved')
    remain_qty = fields.Float(string='Available')
    warehouse = fields.Char(string='Warehouse')
    order_line_id = fields.Many2one('sale.order.line')




