from collections import defaultdict
from flask import Flask, render_template
import locale
from stock_analysis.commands import portfolio
from stock_analysis import constants


locale.setlocale(locale.LC_ALL, '')
app = Flask(__name__)
portfolio_commands = portfolio.PortfolioCommands()


card_template = """<div class="ui card"  style="width:auto">
  <div class="content" style="padding:5px 5px 5px 5px;font-size:small">{key}</div>
  <div class="content" style="padding:5px 5px 5px 5px;font-size:medium" id={key}_card>{value}</div>
</div>"""


@app.route('/')
def home():
    return "Hello, World!"  # return a string


@app.route('/static')
def static_testing():
    return render_template('static.html')


@app.route('/portfolio')
def portfolio():
    basic_details = portfolio_commands.get_portfolio_details(1)
    order_comps = portfolio_commands.get_benchmark_comparison_to_order_prices(1)
    table_lines = _make_table_from_details(basic_details)
    cards_lines = _make_cards_summary(basic_details, order_comps)
    return render_template(
        'portfolio.html',
        table_lines=table_lines,
        cards_lines=cards_lines,
        stock_to_weight={k: sum(o[2] for o in v) for k, v in order_comps.items()},
    )


def _make_table_from_details(details):
    fields = details[0]._fields
    table_lines = ['<table class="ui sortable celled table table-hover">']
    table_lines.append('<thead>')
    table_lines.append('<th data-sort="string">{}</th>'.format(fields[0]))
    for field in fields[1:]:
        table_lines.append('<th data-sort="customfloat">{}</th>'.format(field))
    table_lines.append('</thead>')
    table_lines.append('<tbody>')
    for detail in details:
        table_lines.append('<tr onclick=highlight_row(this)>')
        table_lines.append('<td>{}</td>'.format(detail[0]))
        for field in fields[1:]:
            td_data = detail.__getattribute__(field)
            table_lines.append(_make_td_html(td_data, field))
        table_lines.append('</tr>')
    table_lines.append('</tbody>')
    table_lines.append('</table>')
    return table_lines


def _make_td_html(td_data, field):
    is_percent = field.endswith('p')
    is_highlighted = 'gain' in field

    if is_highlighted:
        tag_coloring = 'style="color:green;text-align:right;"' if td_data >= 0 \
            else 'style="color:red;text-align:right;"'
        td_tag = '<td class="{}" {}>'.format(field, tag_coloring)
    else:
        td_tag = '<td class="{}" style="text-align:right;">'.format(field)

    td_data_formatted = '{0:.2f}%'.format(td_data) if is_percent \
        else '$' + locale.format('%.2f', td_data, grouping=True)
    return '{0}{1}</td>'.format(td_tag, td_data_formatted)


def _make_cards_summary(details, order_comps):
    summary = defaultdict(float)
    for detail in details:
        summary['gain1dp'] += detail.gain1dp * detail.portfoliop / 100
        summary['gainp'] += detail.gainp * detail.portfoliop / 100
        summary['gain1dv'] += detail.gain1dv
        summary['gainv'] += detail.gainv
        summary['value'] += detail.value
    for k in summary.keys():
        if k.endswith('p'):
            summary[k] = '{0:.2f}%'.format(summary[k])
        elif 'gain' in k or k == 'value':
            summary[k] = '$' + locale.format('%.2f', summary[k], grouping=True)
    cards = []
    for card_title in ['value', 'gainp', 'gainv', 'gain1dp', 'gain1dv']:
        cards.append(card_template.format(key=card_title, value=summary[card_title]))

    comps = defaultdict(float)
    for ticker, orders in order_comps.items():
        for bench_ticker in constants.BENCHMARK_TICKERS:
            comps[bench_ticker] += sum(o[1][bench_ticker] * o[2] for o in orders)

    for bench_ticker, vs_percent in comps.items():
       value = '{0:.2f}%'.format(vs_percent)
       cards.append(card_template.format(key='vs. ' + bench_ticker, value=value))

    return cards


if __name__ == '__main__':
    app.run(debug=True)
