odoo.define('website_ko_options.datepicker', function(require) {
    "use strict";

    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var ServicesMixin = require('web.ServicesMixin');
    var Widget = require('web.Widget');

    var _t = core._t;

    var DateWidget = Widget.extend({
        template: 'website_ko_options.datepickerjs',
        xmlDependencies: ['/website_ko_options/static/src/xml/ko_base.xml'],
        type_of_date: "date",
        events: {
            'dp.change': 'changeDatetime',
            'dp.show': '_onShow',
            'change .o_website_datepicker_input': 'changeDatetime',
        },
        /**
         * @override
         */
        init: function(parent, field_options, options) {
            this._super.apply(this, arguments);

            this.name = field_options.name;
            this.options = _.defaults(options || {}, {
                format: this.type_of_date === 'datetime' ? time.getLangDatetimeFormat() : time.getLangDateFormat(),
                minDate: moment({ y: 1900 }),
                maxDate: moment().add(200, "y"),
                calendarWeeks: true,
                icons: {
                    time: 'fa fa-clock-o',
                    date: 'fa fa-calendar',
                    next: 'fa fa-chevron-right',
                    previous: 'fa fa-chevron-left',
                    up: 'fa fa-chevron-up',
                    down: 'fa fa-chevron-down',
                    close: 'fa fa-times',
                },
                locale: moment.locale(),
                allowInputToggle: true,
                keyBinds: null,
                widgetParent: 'body',
                useCurrent: false,
            });
            console.log(this.options);
        },
        /**
         * @override
         */
        start: function() {
            this.$input = this.$('input.o_website_datepicker_input');
            this.$input.datetimepicker(this.options);
            this.picker = this.$input.data('DateTimePicker');
            console.log(this.picker);
            this.$tz = this.$('input.o_timezone');
            this._setReadonly(false);
        },
        /**
         * @override
         */
        destroy: function() {
            this.picker.destroy();
            this._super.apply(this, arguments);
        },

        //--------------------------------------------------------------------------
        // Public
        //--------------------------------------------------------------------------

        /**
         * set datetime value
         */
        changeDatetime: function() {
            if (this.isValid()) {
                var oldValue = this.getValue();
                this._setValueFromUi();
                var newValue = this.getValue();
                var hasChanged = !oldValue !== !newValue;
                if (oldValue && newValue) {
                    var formattedOldValue = oldValue.format(time.getLangDatetimeFormat());
                    var formattedNewValue = newValue.format(time.getLangDatetimeFormat())
                    if (formattedNewValue !== formattedOldValue) {
                        hasChanged = true;
                    }
                }
                if (hasChanged) {
                    // The condition is strangely written; this is because the
                    // values can be false/undefined
                    var value = this.getValue();
                    console.log(value.format(this.options.format));
                    console.log(new Date().getTimezoneOffset(value));
                    this.$tz.val(value && value.add(new Date().getTimezoneOffset(value), 'minutes').format(this.options.format));
                    console.log(this.$tz.val());
                    // this.trigger("datetime_changed");
                }
            }
        },
        /**
         * @returns {Moment|false}
         */
        getValue: function() {
            var value = this.get('value');
            return value && value.clone();
        },
        /**
         * @returns {boolean}
         */
        isValid: function() {
            var value = this.$input.val();
            if (value === "") {
                return true;
            } else {
                try {
                    this._parseClient(value);
                    return true;
                } catch (e) {
                    return false;
                }
            }
        },
        /**
         * @param {Moment|false} value
         */
        setValue: function(value) {
            this.set({ 'value': value });
            var formatted_value = value ? this._formatClient(value) : null;
            this.$input.val(formatted_value);
            if (this.picker) {
                this.picker.date(value || null);
            }
        },

        //--------------------------------------------------------------------------
        // Private
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {Moment} v
         * @returns {string}
         */
        _formatClient: function(v) {
            return field_utils.format[this.type_of_date](v, null, { timezone: false });
        },
        /**
         * @private
         * @param {string|false} v
         * @returns {Moment}
         */
        _parseClient: function(v) {
            return field_utils.parse[this.type_of_date](v, null, { timezone: false });
        },
        /**
         * @private
         * @param {boolean} readonly
         */
        _setReadonly: function(readonly) {
            this.readonly = readonly;
            this.$input.prop('readonly', this.readonly);
        },
        /**
         * set the value from the input value
         *
         * @private
         */
        _setValueFromUi: function() {
            var value = this.$input.val() || false;
            this.setValue(this._parseClient(value));
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * set the date of the picker by the current date or the today date
         *
         * @private
         */
        _onShow: function() {
            //when opening datetimepicker the date and time by default should be the one from
            //the input field if any or the current day otherwise
            if (this.$input.val().length !== 0 && this.isValid()) {
                var value = this._parseClient(this.$input.val());
                this.picker.date(value);
                this.$input.select();
            }
        },
    });

    var DateTimeWidget = DateWidget.extend({
        type_of_date: "datetime",
        init: function() {
            this._super.apply(this, arguments);
            this.options = _.defaults(this.options, {
                showClose: true,
            });
        },
    });

    // console.log(weContext.get());
    return {
        DateWidget: DateWidget,
        DateTimeWidget: DateTimeWidget,
    };
});