odoo.define('website_ko_options.website_sale', function(require) {
    "use strict";

    var DateTimePicker = require('website_ko_options.datepicker');
    var utils = require('website_ko_options.utils');
    require('web.dom_ready');
    require('website_sale.website_sale');

    utils.onElement['inserted']('body', '.o_website_field', function(element) {
        var datepicker;
        if ($(element).data('type') == "date") {
            datepicker = new DateTimePicker.DateWidget(null, { name: $(element).data('name') });
        } else {
            datepicker = new DateTimePicker.DateTimeWidget(null, { name: $(element).data('name') });
        }
        datepicker.appendTo($(element)).done(function() {
            console.log(datepicker.$el);
        });
    });
});