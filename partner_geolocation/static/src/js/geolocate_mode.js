odoo.define('partner_geolocation.geolocate_mode', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Widget = require('web.Widget');
    var Session = require('web.session');
    var QWeb = core.qweb;


    var GeolocateMode = Widget.extend({
        events: {
            "click .o_partner_geolocation_button_partners": function() { this.do_action('partner_geolocation.res_partner_geolocation_action_kanban'); },
        },

        start: function() {
            var self = this;
            self.session = Session;
            var def = this._rpc({
                    model: 'res.company',
                    method: 'search_read',
                    args: [
                        [
                            ['id', '=', this.session.company_id]
                        ],
                        ['name']
                    ],
                })
                .then(function(companies) {
                    self.company_name = companies[0].name;
                    self.company_image_url = self.session.url('/web/image', { model: 'res.company', id: self.session.company_id, field: 'logo', });
                    self.$el.html(QWeb.render("PartnerGeolocationGeolocateMode", { widget: self }));
                });

            return $.when(def, this._super.apply(this, arguments));
        },
    });

    core.action_registry.add('partner_geolocation_geolocate_mode', GeolocateMode);

    return GeolocateMode;

});