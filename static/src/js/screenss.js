odoo.define('home_delivery_odoo_pos_website_mobile_pragtech.ShowHomeDeliveryButton', function(require) {
    "use strict";
    console.log("heeeeeeeeeeeeeeeeeeeeee");
    var models = require('point_of_sale.models');
    const ProductScreen = require('point_of_sale.ProductScreen');
    var core = require('web.core');
    const { Gui } = require('point_of_sale.Gui');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');
    var _t = core._t;

    class ShowHomeDeliveryButton extends PosComponent {

        constructor() {
            super(...arguments);
            console.log("heeeeeeeeeeeeeeeeeeeeee222");
        }
//        renderElement (){
//        var self = this;
        this.showPopup('HomeDeliveryOrderPopupWidget');
//            console.log("heeeeeeeeeeeeeeeeeeeeee333")
//        }
    };
    ShowHomeDeliveryButton.template = 'ShowHomeDeliveryButton'
    Registries.Component.add(ShowHomeDeliveryButton);
    return ShowHomeDeliveryButton;
});