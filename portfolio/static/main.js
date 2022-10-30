var selc = document.getElementsByClassName("n_slec");
for (let i = 0; i < selc.length; i++) {
    selc[i].addEventListener("click", function() {
        var list = document.querySelectorAll(".n_slec.slec");
        count = list.length;
        if (count < 10) {
            this.classList.toggle("slec");
        }
        else {
            if (this.classList.contains("slec")) {
                this.classList.toggle("slec");
            }
            else {
                alert("You can select a maximmum of 10 stocks");
            }
        }
    });
}
msg  = [];
var bias_show = document.getElementById("bias_selec");
var d3 = document.getElementById("d3");
d3.addEventListener("change", function() {
    bias_show.style.visibility = "visible";
});
var post = document.getElementById("post");
function render_rest(cov_mat, curr_dat, bias_arr, stock_list) {
    htm2 = "<table id = \"cov_table\">"

    for (row in cov_mat) {
        htm2 += "<tr>" 
        for (col in cov_mat[row]) {
            tmp = String(cov_mat[row][col])
            htm2 += "<td>" + tmp.slice(0, 8) + "</td>"
        }
        htm2 += "</tr>"
    }
    htm2 +="  </table>"

    htm3 = "<table id = \"price_table\"> <tr> "
    for (let i = 0; i < curr_dat.length; i++) {
        htm3 += "<td>" + curr_dat[i][0] + "</td>"
    }
    htm3 += " </tr><tr> "
    for (let i = 0; i < curr_dat.length; i++) {
        htm3 += "<td>" + curr_dat[i][1] + "</td>"
    }
    htm3 += "</tr></table>"

    htm4  = "<table class = \"display_stock\" id = \"rand_bias\" style = \"visibility : visible\" checked> <tr>"
    for (let i = 0; i < stock_list.length; i++) {
        if (bias_arr[i] == 1) {
            htm4 += "<td class = \"biased\">" + stock_list[i] + "</td>"
        }
        else if (bias_arr[i] == 0) {
            htm4 += "<td class = \"biased\">" + stock_list[i] + "</td>"
        }
        else {
            htm4 += "<td class = \"unbiased\">" + stock_list[i] + "</td>"
        }
    }
    htm4 += "</tr><tr>"
    for (let i = 0; i < bias_arr.length; i++) {
        if (bias_arr[i] == 1) {
            htm4 += "<td class = \"biased\"> 1 </td>"
        }
        else if (bias_arr[i] == 0) {
            htm4 += "<td class = \"biased\">0</td>"
        }
        else {
            htm4 += "<td class = \"unbiased\">*</td>"
        }
    }
    htm4 += "</tr></table>"
    
    htm5 = "<table id = \"user_bias\" class = \"display_stock\" style = \"visibility : hidden\"><tr>"
    for (let i = 0; i < stock_list.length; i++) {
        htm5 += "<td>" + stock_list[i] + "</td>"
    }
    htm5 += "</tr><tr>"
    for (let i = 0; i < stock_list.length; i++) {
        htm5 += "<td><input type = \"number\" id = \"bias_" + stock_list[i] + "\" value = 2></td>"
    }
    htm5 += "</tr></table>"

    el1 = document.getElementById("cov_table");
    el2 = document.getElementById("curr_pdata");
    el3 = document.getElementById("rand_bias_h");
    el4 = document.getElementById("user_bias_h");
    el1.innerHTML = htm2;
    el2.innerHTML = htm3;
    el3.innerHTML = htm4;
    el4.innerHTML = htm5;


    show1 = document.getElementById("Selection2");
    show2 = document.getElementById("Selection3");
    show1.style.opacity = 1;
    show2.style.opacity = 1;

    document.getElementById("curr_price_h").children[0].innerText += "( on " + document.getElementById("dt2").value + " )" ;
}

bias_el = document.getElementsByName("bias_opt");
for (let i = 0; i < bias_el.length; i++) {
    bias_el[i].addEventListener("click", function() {
        if (this.id == "rV") {
            document.getElementById("rand_bias").style.visibility = "visible";
            document.getElementById("user_bias").style.visibility = "hidden";
        }
        else {
            document.getElementById("rand_bias").style.visibility = "hidden";
            document.getElementById("user_bias").style.visibility = "visible";
        }
    });
}
post.addEventListener("click", function() {
    var i;
    var selected = document.getElementsByClassName("slec");
    var date_st = document.getElementById("dt1").value;
    var date_end = document.getElementById("dt2").value;
    if (selected.length < 2 || date_st == "" || date_end == "") {
        alert("Please select at least two stocks and the date range");
    }
    else {
        for (i = 0; i < selected.length; i++) {
            msg.push(selected[i].id);
        }
        msg.push(date_st);
        msg.push(date_end);
        $.ajaxSetup({
        headers: { "X-CSRFToken": csrf_token }
        });
        $.ajax({
            type: "POST",
            url: "/stocks",
            data: JSON.stringify(msg),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function(data){
                //alert("Success");
                cov_mat = data['cov_mat'];
                curr_price = data['curr_price'];
                bias_arr = data['bias_arr'];
                stock_list = data['stock_names'];
                render_rest(cov_mat, curr_price, bias_arr, stock_list);
            },
            failure: function(errMsg) {
                alert(errMsg);
            }
        });
    }
});  

var calc = document.getElementsByClassName("calc");
for (let i = 0; i < calc.length; i++) {
    calc[i].addEventListener("click", function() {
        this.style.backgroundColor = "#ffffff";
        var budget = document.getElementById("budget").value;
        var bias = document.getElementById("rand_bias");
        var user_bias = document.getElementById("user_bias");
        var stock_list = document.getElementsByClassName("display_stock")[0].children[0].children[0].children;
        var user_bias_list = [];
        var model_confidence = document.getElementById("pConvergence").value;
        if (budget == "") {
            alert("Please enter a budget");
        }
        else {
            if (user_bias.style.visibility == "hidden") {
                for (let i = 0; i < stock_list.length; i++) {
                    user_bias_list.push(2);
                }
            }
            else {
                for (let i = 0; i < stock_list.length; i++) {
                    var id = "bias_" + stock_list[i].innerHTML;
                    var val = document.getElementById(id).value;
                    if (val == 1) {
                        user_bias_list.push(1);
                    }
                    else if (val == 0) {
                        user_bias_list.push(0);
                    }
                    else {
                        user_bias_list.push(2);
                    }
                }
            }
            bias_el = document.getElementsByName("bias_opt");
            for (let i = 0; i < bias_el.length; i++) {
                if (bias_el[i].checked) {
                    if (bias_el[i].id == "rV") {
                        var bias = bias.children[0].children[1].children;
                        for (let i = 0; i < bias.length; i++) {
                            if (bias[i].innerText == "1") {
                                user_bias_list[i] = 1;
                            }
                            else if (bias[i].innerText == "0") {
                                user_bias_list[i] = 0;
                            }
                        }
                    }
                }
            }
            method  = this.id;
            function setGreen(method){
                document.getElementById(method).style.backgroundColor = "#00ff00";
            }
            var msg = [user_bias_list, budget, method, model_confidence];
            console.log(user_bias_list);
            $.ajaxSetup({
            headers: { "X-CSRFToken": csrf_token }
            });
            $.ajax({
                type: "POST",
                url: "/calc",
                data: JSON.stringify(msg),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(data){
                    //alert("Success");
                    setGreen(method);
                    var final_res = data['final_res'];
                    var stock_names = data['stock_names'];
                    var bias_arr = data['bias_arr'];
                    console.log(bias_arr);
                    var htm = "<table id = \"res_table\"><tr>";
                    for (let i = 0; i < stock_names.length; i++) {
                        if (bias_arr[i] == final_res[i]) {
                            htm += "<td class = \"biased\">" + stock_names[i] + "</td>";
                        }
                        else if (final_res[i] == 0) {
                            htm += "<td class = \"exc\">" + stock_names[i] + "</td>";
                        }
                        else {
                            htm += "<td class = \"inc\">" + stock_names[i] + "</td>";
                        }
                    }
                    htm += "</tr><tr>"
                    for (let i = 0; i < bias_arr.length; i++) {
                        if (bias_arr[i] == 1 && final_res[i] == 1) {
                            htm += "<td class = \"biased\"> 1 </td>"
                        }
                        else if (bias_arr[i] == 0 && final_res[i] == 0) {
                            htm += "<td class = \"biased\">0</td>"
                        }
                        else if (final_res[i] == 0) {
                            htm += "<td class = \"exc\">0</td>"
                        }
                        else {
                            htm += "<td class = \"inc\">1</td>"
                        }
                    }
                    htm += "</tr></table>"
                    
                    document.getElementById("final_res").innerHTML += htm;
                },
                failure: function(errMsg) {
                    alert(errMsg);
                }
            });
        }
    });
}