//openerp.hubi = function(instance) {
// var ListView = instance.web.ListView;
odoo.define('hubi.import_buttons', function (require) {
"use strict";
var core = require('web.core');
var ListView = require('web.ListView');
var QWeb = core.qweb;

 ListView.include({
 render_buttons: function() {

// GET BUTTON REFERENCE
 this._super.apply(this, arguments)
 if (this.$buttons) {
 var btn = this.$buttons.find('.email_button')
 }

// PERFORM THE ACTION
 btn.on('click', this.proxy('send_email'))

},
 send_email: function() {
 new instance.web.Model('account.invoice')
 .call('invoice_send_email', [[]])
 .done(function(result) {
 alert('done')
 })
 }
 });
}