odoo.define('account.withholding', function (require) {
    "use strict";
    
    var AbstractField = require('web.AbstractField');
    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var field_utils = require('web.field_utils');

    var QWeb = core.qweb;
    var _t = core._t;
    
    var ShowWtaxWidget = AbstractField.extend({
        // events: _.extend({
        //     'click .outstanding_credit_assign': '_onOutstandingCreditAssign',
        // }, AbstractField.prototype.events),
        supportedFieldTypes: ['char'],
        _render: function() {
            var self = this;
            var info = JSON.parse(this.value);
            if (!info) {
                this.$el.html('');
                return;
            }
            _.each(info.content, function (k, v){
                k.index = v;
                k.amount = field_utils.format.float(k.amount, {digits: k.digits});
                if (k.date){
                    k.date = field_utils.format.date(field_utils.parse.date(k.date, {}, {isUTC: true}));
                }
            });
            console.log('loggg info'+ info.title);
            this.$el.html(QWeb.render('ShowWhtaxInfo', {
                lines: info.content,
                title: info.title
            }));
        },

    });
    
    fieldRegistry.add('whtax', ShowWtaxWidget);
    
    return {
        ShowWtaxWidget: ShowWtaxWidget,
    };
    });