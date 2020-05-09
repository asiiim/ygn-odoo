odoo.define('partner_geolocation.location_message', function(require) {
    "use strict";

    var core = require('web.core');
    var Widget = require('web.Widget');

    var _t = core._t;


    var LocationMessage = Widget.extend({
        template: 'PartnerGeolocationLocationMessage',
        events: {
            "click .o_partner_geolocation_button_dismiss": function() { this.do_action(this.next_action, { clear_breadcrumbs: true }); },
        },

        init: function(parent, action) {
            var self = this;
            this._super.apply(this, arguments);

            // if no correct action given (due to an erroneous back or refresh from the browser), we set the dismiss button to return
            // to the (likely) appropriate menu, according to the user access rights
            if (!action.partner) {
                self.next_action = 'partner_geolocation.partner_geolocation_action_geolocate_mode';
                return;
            }

            this.next_action = action.next_action || 'partner_geolocation.partner_geolocation_action_geolocate_mode';
            this.partner = action.partner;
            // We receive the geolocation in logitude and latitude
            // This widget only deals with display, which should be in map but for now text
            // geolocation displayed in the location message template.
            this.partner.partner_latitude = this.partner.partner_latitude;
            this.partner.partner_longitude = this.partner.partner_latitude;
            this.previous_geolocate_change_date = action.previous_geolocate_change_date && moment.utc(action.previous_geolocate_change_date).local();
            this.partner_name = action.partner_name;
        },

        start: function() {
            console.warn(this.partner);
            if (this.partner) {
                this.welcome_message();
            }
        },

        welcome_message: function() {
            var self = this;
            this.return_to_main_menu = setTimeout(function() { self.do_action(self.next_action, { clear_breadcrumbs: true }); }, 5000);

            if (this.partner.previous_geolocate_change_date) {
                this.$('.o_partner_geolocation_message_message').prepend(_t("Location has been changed for"));
            } else {
                this.$('.o_partner_geolocation_message_message').prepend(_t("Location has been set for the first time for"));
            }
        },

        destroy: function() {
            clearTimeout(this.return_to_main_menu);
            this._super.apply(this, arguments);
        },
    });

    core.action_registry.add('partner_geolocation_location_message', LocationMessage);

    return LocationMessage;

});