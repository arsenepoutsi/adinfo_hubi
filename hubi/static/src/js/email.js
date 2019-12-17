odoo.define('hubi.tree_view_button', function (require){
"use strict";
    var ListView = require('web.ListView');
    var Model = require('web.Model');
    ListView.include({
        render_buttons: function() {
            this._super.apply(this, arguments)
            if (this.$buttons) {
                var btn = this.$buttons.find('.email_button')
                btn.on('click', this.proxy('send_email'))
            }
       },
        send_email: function() {
            new Model('account.invoice')
                .call('invoice_send_email', [[]])
                .done(function(result) {
                    alert('done')
                })
        }
    });
});