# import the Flask class from the flask module
from flask import Flask, render_template
from stock_analysis.commands import portfolio

# create the application object
app = Flask(__name__)
portfolio_commands = portfolio.PortfolioCommands()


# use decorators to link the function to a url
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


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
