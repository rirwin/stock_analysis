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

function highlight_row(ev) {
    var wasActiveRow = ev.target.parentElement.classList.contains('active');
    ev.target.parentElement.classList.toggle('active');
    
    // if clicked row was highlighted and shift key pressed
    // highlight all consecutive unhighlighted rows above
    if ( !wasActiveRow && ev.shiftKey){
        var table_div = document.getElementById("main_table_div");
        var rows = table_div.getElementsByTagName("tr");
        var this_row_i;
        var row_i;
        for (row_i = 0; row_i < rows.length; row_i++)
            if (rows[row_i] == ev.target.parentElement)
                this_row_i = row_i;

        row_i = this_row_i - 1;
        while (row_i > 0 && !rows[row_i].classList.contains('active')) {
            rows[row_i].classList.toggle('active');
            row_i--;
        }
    } 
    calculate_cards();
}

function calculate_cards() {
    var detail_classes = [
        'value', 'gainp', 'gainv', 'gain1dp', 'gain1dv', 'gainspyp', 'gainqqqp', 'gaindiap'
    ]
    var weight_map = {};

    if ( should_calculate_all_cells() )
        weight_map = stock_to_weight;
    else
        weight_map = calculate_weights();

    for ( var class_i = 0; class_i < detail_classes.length; class_i++ ) {
        var detail_class = detail_classes[class_i];
        var card_value = calculate_card_value(detail_class, weight_map);
        update_card_with_value(detail_class, card_value); 
    }
}

function calculate_card_value(detail_class, ticker_to_weight){
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    var total = 0;
    for (var row_i = 1; row_i < rows.length; row_i++) {
        var ticker = rows[row_i].cells[0].innerHTML;
        if ( ticker in ticker_to_weight ) {
            var td_value = parseFloat(rows[row_i].getElementsByClassName(detail_class)[0].innerHTML.replace(/[$%,]/g, ''), 10);
            if ( detail_class.endsWith('p') )
                td_value *= ticker_to_weight[ticker];
            total += td_value;
        }
    }
    return total;
}

function update_card_with_value(detail_class, card_value) {
    var td_value = get_number_with_commas(parseFloat(card_value).toFixed(2));
    if ( detail_class.endsWith('p') )
        td_value = td_value + '%';
    else
        td_value = '$' + td_value;
    document.getElementById(detail_class + "_card").innerHTML = td_value;
}

function get_number_with_commas(x){
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function should_calculate_all_cells(){
    var table_div = document.getElementById("main_table_div");
    var rows = table_div.getElementsByTagName("tr");
    active_cell_count = 0;
    for (var row_i = 1; row_i < rows.length; row_i++) {
        if ( rows[row_i].classList.contains('active') ) 
            active_cell_count++;
    }
    if ( active_cell_count == rows.length - 1 ||  active_cell_count == 0)
        return true;
    return false;
}

function calculate_weights() {
    var table_div = document.getElementById("main_table_div");
    var dynamic_weights = {};
    var denom = 0;
    var rows = table_div.getElementsByTagName("tr");
    for (var row_i = 1; row_i < rows.length; row_i++) {
        if ( rows[row_i].classList.contains('active') ) {
            var ticker = rows[row_i].cells[0].innerHTML;
            denom = denom + stock_to_weight[ticker];
            dynamic_weights[ticker] = stock_to_weight[ticker];
        }
    }
    for (var key in dynamic_weights) {
        dynamic_weights[key] /= denom;
    }
    return dynamic_weights;
}
