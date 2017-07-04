# import the Flask class from the flask module
from flask import Flask, render_template
from stock_analysis.commands import portfolio

# create the application object
app = Flask(__name__)
portfolio_commands = portfolio.PortfolioCommands()


@app.route('/')
def home():
    return "Hello, World!"  # return a string


@app.route('/table_sorted')
def table_sorted():
    return render_template('semantic.html')


@app.route('/welcome')
def welcome():
    details = portfolio_commands.get_portfolio_details(1)
    return render_template(
        'welcome.html',
        fields=details[0]._fields,
        details=details,
    )


@app.route('/hello')
def hello():
    details = portfolio_commands.get_portfolio_details(1)
    table_lines = _make_table_from_details(details)
    return render_template(
        'hello.html',
        table_lines=table_lines,
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
        table_lines.append('<tr>')
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
    is_highlighted = '1d' in field

    if is_highlighted:
        tag_coloring = 'style="color:green;text-align:right;"' if td_data >= 0 \
            else 'style="color:red;text-align:right;"'
        td_tag = '<td {}>'.format(tag_coloring)
    else:
        td_tag = '<td style="text-align:right;">'

    td_template = '{0:.2f}%' if is_percent else '${0:.2f}'
    td_data_formatted = td_template.format(td_data)
    return '{0}{1}</td>'.format(td_tag, td_data_formatted)


if __name__ == '__main__':
    app.run(debug=True)
