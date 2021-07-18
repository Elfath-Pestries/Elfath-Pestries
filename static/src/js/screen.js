alert("hiiiiiiiiiiiiiiiiiiiiiiiiiiii");
odoo.define('home_delivery_odoo_pos_website_mobile_pragtech.ShowHomeDeliveryButton', function(require) {
    'use strict';
    alert("huuuuuuuuuuuuuuuuuuuuuuuuuu");
    const PosComponent = require('point_of_sale.PosComponent');
    const Popup = require('point_of_sale.ConfirmPopup');
    const ProductScreen = require('point_of_sale.ProductScreen');
    const PopupWidget = require('point_of_sale.PopupControllerMixin');
    const { useListener } = require('web.custom_hooks');
    const Registries = require('point_of_sale.Registries');

    class ShowHomeDeliveryButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener('click', this.onClick);
        }
        async onClick() {

               await this.showPopup('HomeDeliveryOrderPopupWidget');
        }
    }
    class HomeDeliveryOrderPopupWidget extends Popup {

        constructor() {
            super(...arguments);
        }

        go_back_screen() {
            this.trigger('close-popup');
        }
    }
    HomeDeliveryOrderPopupWidget.template = 'HomeDeliveryOrderPopupWidget';
    ShowHomeDeliveryButton.template = 'ShowHomeDeliveryButton';

    ProductScreen.addControlButton({
        component: ShowHomeDeliveryButton,
        condition: function() {
            return this.env.pos.config.home_delivery;
        },
    });
    Registries.Component.add(HomeDeliveryOrderPopupWidget);
    Registries.Component.add(ShowHomeDeliveryButton);
    return ShowHomeDeliveryButton,HomeDeliveryOrderPopupWidget;
});
