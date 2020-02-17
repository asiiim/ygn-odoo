odoo.define('website_ko_options.utils', function(require) {
    "use strict";

    function onElementInserted(containerSelector, elementSelector, callback) {

        var onMutationsObserved = function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length) {
                    var elements = $(mutation.addedNodes).find(elementSelector);
                    for (var i = 0, len = elements.length; i < len; i++) {
                        callback(elements[i]);
                    }
                }
            });
        };

        var target = $(containerSelector)[0];
        var config = { childList: true, subtree: true };
        var MutationObserver = window.MutationObserver || window.WebKitMutationObserver;
        var observer = new MutationObserver(onMutationsObserved);
        observer.observe(target, config);
    }

    return {
        onElement: {
            inserted: onElementInserted,
        },
    };
});