odoo.define('partner_geolocation.partner_kanban_view_handler', function(require) {
    "use strict";

    var KanbanRecord = require('web.KanbanRecord');

    KanbanRecord.include({
        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @override
         * @private
         */
        _openRecord: function() {
            if (this.modelName === 'res.partner' && this.$el.parents('.o_res_partner_geolocation_kanban').length) {
                var action = {
                    type: 'ir.actions.client',
                    name: 'Confirm',
                    tag: 'partner_geolocation_geolocate_confirm',
                    partner_id: this.record.id.raw_value,
                    partner_name: this.record.display_name.raw_value,
                    partner_street: this.record.street.raw_value,
                    partner_city: this.record.city.raw_value,
                    partner_country_id: this.record.country_id.raw_value,
                    partner_mobile: this.record.mobile.raw_value,
                };
                this.do_action(action);
            } else {
                this._super.apply(this, arguments);
            }
        }
    });

});