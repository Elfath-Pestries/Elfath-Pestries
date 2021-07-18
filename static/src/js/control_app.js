odoo.define("home_delivery_odoo_pos_website_mobile_pragtech.control_app", function(require){
	"use strict";

	$(document).ready(function(){
	    $('#driver_message').hide();

             // Collect Payment
        $('.collect_payment_pos').click(function(e){
            var order_id = $(this).attr('order_id');
            var order_source = "ERP";
            if($(this).data('orderSource') == "POS")
            {
                order_source = $(this).data('orderSource');
            }
            var value = {
                "order_id" : order_id,
                "order_source" : order_source,
            }
            $.ajax({
                url : "/collect-payment-pos",
                data : value,
                cache : "false",

                success : function(res) {
                    var vals = $.parseJSON(res);
                    window.location.reload();
                },

                Error : function(x, e) {
                    alert("Some error");
                }
            });
        });

	    $('.joblist_cancel_pos_order').on('click', function(){
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id,
	    	}
	    	$.ajax({
	    		url: "/cancel/posorder",
	    		data: data,
	    		success: function(res) {
	    			var res = JSON.parse(res);
	    			if(res.status){
	    				window.history.back();
	    			}
	    		},
	    		Error : function(x, e) {
	    			alert("Some error");
	    		}
	    	});
	    });

	    $('.joblist_delivered_pos_order').on('click', function(){
	        var elem = document.getElementById("delivered_button");
            elem.value = "BACK AT RESTAURANT";
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id,
	    	}
	    	$.ajax({
	    		url: "/delivered/pos_order",
	    		data: data,
	    		success: function(res) {
	    			var res = JSON.parse(res);
	    			if(res.status){
	    				window.history.back();
	    			}
	    		},
	    		Error : function(x, e) {
	    			alert("Some error");
	    		}
	    	});
        });

        $('.joblist_cancel_pos_order_driver').on('click', function(){
	    	var order_id = $(this).data('order_id');
	    	var data = {
	    		'order_id' : order_id
	    	}
	    	$.ajax({
	    		url: "/driver/cancel/pos_order",
	    		data: data,
	    	})
	    	.done(function(res){
                var res = JSON.parse(res);
                if(res.status){
                    window.history.back();
                }
            })
            .fail(function(resp){
                alert("Something went wrong")
            });
	    });

	    $('.joblist_pos_order_pay_now').on('click', function (){
            var elem = document.getElementById("pay_now_button1");
            var order_number = document.getElementById("order_number").value
            elem.value = "PAID";
            var payment_status = elem.value
            var value = {
            'payment_status': payment_status,
            'order_number': order_number
            }

             $.ajax({
                url : '/paid/pos_order/status',
                data : value
            })
            .done(function(res){
               $('.joblist_pos_order_pay_now').hide()
               elem.value = "PAID";
            })
            .fail(function(resp){
                alert("Something went wrong!!!!!")
            })
         });

         $('#selectPayment').change(function(event){
            var selectPayment = document.getElementById("selectPayment")
            var order_number = document.getElementById("order_number").value
            var selectedValue = selectPayment.options[selectPayment.selectedIndex].value;
            var value = {
            'selectedValue': selectedValue,
            'order_number': order_number
            }
            $.ajax({
                url : '/select/payment/pos/status',
                data : value
            })
	    });

        //Load driver on modal

	    $('#driver_msg_issue').on('show.bs.modal', function(e) {
	    	$('#driver_message').show();
	    });

	    $('#driver_msg_issue .confirm_driver').click(function(e){
            var message_driver = $("#message_driver1").val()
			var driver_id = parseInt($('input[name=driver_radio]:checked').val())
			var order_id = parseInt($('input[name=driver_radio]:checked').attr('id'))
			var warehouse_id = parseInt($('input[name=warehouse_id]').val())
			var driver_name_tr = $('#driver_name').val();
			var value = {
					"payment_status_driver" : message_driver,
            }
            $.ajax({
                url : "/driver/issue/message",
                data : value,
                cache : "false",
                success : function(res) {
                    var vals = $.parseJSON(res)
                    var new_driver_name=$('input[name=driver_radio]:checked').data('text');
                    $('#'+driver_name_tr +' > #order_driver_name > span').text(driver_name_tr);
                    $('#driver_msg_issue').modal('hide');
                    alert("Message Sent!!!");
//						window.location="/page/manage-sale-order-delivery";
                },
                Error : function(x, e) {
                    alert("Some error");
                }
            });
		});


        $('.driver_joblist_back').on('click',function(){
            window.history.back()
        })

        $('.joblist_back').on('click',function(){
            window.history.back();
        })
	});

});