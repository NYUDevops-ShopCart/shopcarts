$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************
    function update_form_data(res) {
        $("#customer_id").val(res.customer_id);
        $("#product_id").val(res.product_id);
        $("#text").val(res.text);
        $("#quantity").val(res.quantity);
        $("#price").val(res.price);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#customer_id").val("");
        $("#product_id").val("");
        $("#text").val("");
        $("#quantity").val("");
        $("#price").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    
    // ****************************************
    // Create a Shopcart
    // ****************************************
    
    $("#create-btn").click(function () {

        var customer_id = $("#customer_id").val();
        var product_id = $("#product_id").val();
        var quantity = $("#quantity").val();
        var price = $("#price").val();
        var text = $("#text").val();

        var data = {
            "customer_id": customer_id,
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
            "text": text
        };

        var ajax = $.ajax({
            type: "POST",
            url: "/shopcarts/" + customer_id,
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseText)
        });
    });


    // ****************************************
    // Update a Pet
    // ****************************************

    $("#update-btn").click(function () {

        var pet_id = $("#pet_id").val();
        var name = $("#pet_name").val();
        var category = $("#pet_category").val();
        var available = $("#pet_available").val() == "true";

        var data = {
            "name": name,
            "category": category,
            "available": available
        };

        var ajax = $.ajax({
                type: "PUT",
                url: "/pets/" + pet_id,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve a Shopcart
    // ****************************************

    $("#read-btn").click(function () {

        var customer_id = $("#customer_id").val();
        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/" + customer_id + "/" + product_id,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            if(!$.isEmptyObject(res)) {
                $("#search_results").empty();
                $("#search_results").append('<table class="table-striped" cellpadding="10">');
                var header = '<tr>'
                header += '<th style="width:10%">Customer_ID</th>'
                header += '<th style="width:40%">Product_ID</th>'
                header += '<th style="width:40%">Item_Text</th>'
                header += '<th style="width:40%">Quantity</th>'
                header += '<th style="width:10%">Price</th></tr>'
                $("#search_results").append(header);
                var firstItem = "";
                var item = res;
                var row = "<tr><td>"+item.customer_id+"</td><td>"+item.product_id+"</td><td>"+item.text+"</td><td>"+item.quantity+"</td><td>"+item.price +"</td></tr>" ;
                $("#search_results").append(row);
                firstItem = item;
                flash_message("Read shopcart Success!")
            }
            
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

        console.log("abcdefg")

    });
    
    $("#delete-btn").click(function () {

        var customer_id = $("#customer_id").val();
        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "DELETE",
            url: "/shopcarts/" + customer_id + "/" + product_id,
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Item has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Move the product to checkout start
    // ****************************************

    $("#order-btn").click(function () {
        var customer_id = $("#customer_id").val();
        var product_id = $("#product_id").val();

        var ajax = $.ajax({
            type: "PUT",
            url: "/shopcarts/" + customer_id + "/" + product_id + "/checkout",
            contentType: "application/json"
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been moved to Orders!")
        });

        ajax.fail(function(res){    
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#pet_id").val("");
        clear_form_data()
    });


    // ****************************************
    // List shopcart
    // ****************************************

    $("#list-btn").click(function () {

        var customer_id = $("#customer_id").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/" + customer_id
        })
        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Customer_ID</th>'
            header += '<th style="width:40%">Product_ID</th>'
            header += '<th style="width:40%">Text</th>'
            header += '<th style="width:40%">Quantity</th>'
            header += '<th style="width:10%">Price</th></tr>'
            $("#search_results").append(header);
            var firstItem = "";
            for(var i = 0; i < res.length; i++) {
                var item = res[i];
                var row = "<tr><td>"+item.customer_id+"</td><td>"+item.product_id+"</td><td>"+item.text+"</td><td>"+item.quantity+"</td><td>"+item.price +"</td></tr>" ;
                $("#search_results").append(row);
                if (i == 0) {
                    firstItem = item;
                }
            }

            $("#search_results").append('</table>');
            // copy the first result to the form
            if (firstItem != "") {
                update_form_data(firstItem)
            }
            flash_message("List shopcart Success!")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });
    
    // ****************************************
    // Query shopcart
    // ****************************************

    $("#query-btn").click(function () {

        var customer_id = $("#customer_id").val();
        var price = $("#price").val();

        var ajax = $.ajax({
            type: "GET",
            url: "/shopcarts/" + customer_id + "?price=" + price
        })
        
        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            $("#search_results").append('<table class="table-striped" cellpadding="10">');
            var header = '<tr>'
            header += '<th style="width:10%">Customer_ID</th>'
            header += '<th style="width:40%">Product_ID</th>'
            header += '<th style="width:40%">Text</th>'
            header += '<th style="width:40%">Quantity</th>'
            header += '<th style="width:10%">Price</th></tr>'
            $("#search_results").append(header);
            var firstItem = "";
            for(var i = 0; i < res.length; i++) {
                var item = res[i];
                var row = "<tr><td>"+item.customer_id+"</td><td>"+item.product_id+"</td><td>"+item.text+"</td><td>"+item.quantity+"</td><td>"+item.price +"</td></tr>" ;
                $("#search_results").append(row);
                if (i == 0) {
                    firstItem = item;
                }
            }

            $("#search_results").append('</table>');
            // copy the first result to the form
            if (firstItem != "") {

                update_form_data(firstItem)
            }
            flash_message("Query shopcart Success!")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });
})
