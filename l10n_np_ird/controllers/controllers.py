# -*- coding: utf-8 -*-
from odoo import http

# class L10nNp(http.Controller):
#     @http.route('/l10n_np/l10n_np/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_np/l10n_np/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_np.listing', {
#             'root': '/l10n_np/l10n_np',
#             'objects': http.request.env['l10n_np.l10n_np'].search([]),
#         })

#     @http.route('/l10n_np/l10n_np/objects/<model("l10n_np.l10n_np"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_np.object', {
#             'object': obj
#         })