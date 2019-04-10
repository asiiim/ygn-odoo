odoo.define('google_drive_folder.sidebar', function(require) {
    "use strict";

    /**
     * The purpose of this file is to include the Sidebar widget to add Google
     * Drive related items.
     */

    var Sidebar = require('google_drive.sidebar');


    Sidebar.include({
        /**
         * @override
         */

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {integer} configID
         * @param {integer} resID
         */
        _onGoogleDocItemClicked: function(configID) {
            var self = this;
            var resID = this.env.activeIds[0];
            var domain = [
                ['id', '=', configID]
            ];
            var fields = ['folder', 'google_drive_resource_id', 'google_drive_client_id'];
            this._rpc({
                args: [domain, fields],
                method: 'search_read',
                model: 'google.drive.config',
            }).then(function(configs) {
                var method = "get_google_drive_url";
                if (configs[0].folder) {
                    method = "get_google_drive_folder_url";
                    console.log("inside folder");
                }
                self._rpc({
                    args: [configID, resID, configs[0].google_drive_resource_id],
                    context: self.env.context,
                    method: method,
                    model: 'google.drive.config',
                }).then(function(url) {
                    if (url) {
                        console.log("url is " + url)
                        window.open(url, '_blank');
                    }
                });
            });
        },

    });

    return Sidebar;
});