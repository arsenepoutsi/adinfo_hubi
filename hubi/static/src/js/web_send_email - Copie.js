odoo.define('web_send_email', function (require){
"use strict";
		var core = require('web.core');
		var Sidebar = require('web.Sidebar');
		var ViewManager = require('web.ViewManager');
		var ListController = require('web.ListController');
		var session = require('web.session');
		var QWeb = core.qweb;
		var _t = core._t;

		ListController.include({

			 renderButtons: function($node) {

			 this._super.apply(this, arguments);

					 if (this.$buttons) {
							 let filter_button = this.$buttons.find('.email_button');
							 filter_button && filter_button.click(this.proxy('send_email')) ;
					 }
					 
			 },
        send_email_1: function() {
            new Model('account.invoice')
                .call('invoice_send_email', [[]])
                .done(function(result) {
                    alert('done')
                })
        },
		send_email: function() {
           this.do_warn(_t('Send Email'),
                _t('Verify Email.'));
 
        instance.web.Model('account.invoice')
            .call('invoice_send_email', [[]])
            .done(function(result) {
               alert('done')
            })
		}
    });
});