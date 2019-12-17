odoo.define('hubi.import_buttons', function (require) {
"use strict";

var ListView = require('web.ListView');


ListView.include({
    render_buttons: function() {

        // GET BUTTON REFERENCE
        this._super.apply(this, arguments)
        if (this.$buttons) {
            var btn = this.$buttons.find('.create_product')
        }

        // PERFORM THE ACTION
        btn.on('click', this.proxy('do_new_button'))

    },
    do_new_button: function() {

        instance.web.Model('wiz.create.product.from.category')
            .call('create_product', [[]])
            .done(function(result) {
                < do your stuff, if you don't need to do anything remove the 'done' function >
            })
	}
});
});




