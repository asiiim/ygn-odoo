odoo.define('partner_geolocation.geolocate_confirm', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;


    var GeolocateConfirm = Widget.extend({
        events: {
            "click .o_partner_geolocation_back_button": function() {
                this.do_action(this.next_action, {
                    clear_breadcrumbs: true
                });
            },
            "click .o_partner_geolocation_geolocate_icon": _.debounce(function() {
                this.update_geolocation();
            }, 200, true),
        },

        init: function(parent, action) {
            this._super.apply(this, arguments);
            this.next_action = 'partner_geolocation.partner_geolocation_action_geolocate_mode';
            this.partner_id = action.partner_id;
            this.partner_name = action.partner_name;
            this.partner_street = action.partner_street;
            this.partner_city = action.partner_city;
            this.partner_country_id = action.partner_country_id;
            this.partner_mobile = action.partner_mobile;
        },

        start: function() {
            var self = this;
            self.$el.html(QWeb.render("PartnerGeolocationGeolocateConfirm", {
                widget: self
            }));
            return self._super.apply(this, arguments);
        },

        update_geolocation: function() {
            var self = this;
            var options = {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            };
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(self._manual_geolocate.bind(self), self._getPositionError, options);
            }
        },
        _manual_geolocate: function(position) {
            var self = this;
            this._rpc({
                    model: 'res.partner',
                    method: 'geolocate_manual',
                    args: [
                        [this.partner_id], this.next_action, [position.coords.latitude, position.coords.longitude]
                    ],
                })
                .then(function(result) {
                    if (result.action) {
                        self.do_action(result.action);
                    } else if (result.warning) {
                        self.do_warn(result.warning);
                    }
                });
        },
        _getPositionError: function(error) {
            console.warn('ERROR(${error.code}): ${error.message}');
        },
    });

    core.action_registry.add('partner_geolocation_geolocate_confirm', GeolocateConfirm);

    return GeolocateConfirm;

});