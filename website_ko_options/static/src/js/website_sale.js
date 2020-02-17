odoo.define('website_ko_options.website_sale', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var DateTimePicker = require('website_ko_options.datepicker');
    var utils = require('website_ko_options.utils');
    require('web.dom_ready');
    require('website_sale.website_sale');

    // $(document).ready(function() {
    //     console.log($('#datetimepicker1'));
    //     $('#datetimepicker1').datetimepicker();
    // });

    utils.onElement['inserted']('body', '.o_website_datepicker', function(element) {
        console.log(element);
        // if (e.target.className == 'o_website_datepicker') {
        // var $elems = $('.o_website_datepicker');
        var datepicker;
        // $.each($elems, function(i, elem) {
        if ($(element).data('type') == "date") {
            console.log("inside");
            datepicker = new DateTimePicker.DateWidget({ name: $(element).data('name') });
        } else {
            console.log("inside datetime");
            datepicker = new DateTimePicker.DateTimeWidget({ name: $(element).data('name') });
        }
        datepicker.appendTo($(element)).then(function() {
            console.log($(element));
        });
        // });
        console.log("datetimepicker loaded");
        // }
    });
    // $('body').on('DOMNodeInserted', function(e) {
    //     console.log(e.target.className);
    // });
    // if (!$elem.length) {
    //     return $.Deferred().reject("DOM doesn't contain '.o_branch_location_app'");
    // }
});