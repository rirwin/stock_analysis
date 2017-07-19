function myReset() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    for (row_i = 0; row_i < rows.length; row_i++)
        rows[row_i].classList.remove('active');
    recalculate();
}
function myInvert() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    for (row_i = 1; row_i < rows.length; row_i++)
        rows[row_i].classList.toggle('active')

    recalculate()
}
function myActivate(obj) {
    obj.classList.toggle('active')
    recalculate()
}
function recalculate() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    var active_sum = 0;
    var inactive_sum = 0;
    for (row_i = 1; row_i < rows.length; row_i++) {
        var x = rows[row_i].getElementsByClassName("my_value");
        var count_row = parseFloat(x[0].innerHTML, 10);
        if ( rows[row_i].classList.contains('active') )
            active_sum = active_sum + count_row;
        else
            inactive_sum = inactive_sum + count_row;
    }
    if ( active_sum > 0.1 )
        document.getElementById("market_value").innerHTML = active_sum
    else
        document.getElementById("market_value").innerHTML = inactive_sum
}

