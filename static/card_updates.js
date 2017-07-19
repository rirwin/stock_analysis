function reset_rows() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    for (row_i = 0; row_i < rows.length; row_i++)
        rows[row_i].classList.remove('active');
    calculate_cards();
}
function invert_selection() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    for (row_i = 1; row_i < rows.length; row_i++)
        rows[row_i].classList.toggle('active')
    calculate_cards();
}
function highlight_row(obj) {
    obj.classList.toggle('active')
    calculate_cards()
}
function calculate_cards() {
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var row_i;
    var active_sum = 0;
    var inactive_sum = 0;
    for (row_i = 1; row_i < rows.length; row_i++) {
        var x = rows[row_i].getElementsByClassName("num_shares");
        var count_row = parseFloat(x[0].innerHTML, 10);
        if ( rows[row_i].classList.contains('active') )
            active_sum = active_sum + count_row;
        else
            inactive_sum = inactive_sum + count_row;
    }
    if ( active_sum > 0.1 )
        document.getElementById("value_card").innerHTML = active_sum
    else
        document.getElementById("value_card").innerHTML = inactive_sum
}
