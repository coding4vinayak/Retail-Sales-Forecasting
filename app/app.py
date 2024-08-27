from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from statsmodels.tsa.arima.model import ARIMAResults

app = Flask(__name__)

# Load the ARIMA model (make sure 'arima_model.pkl' exists)
try:
    model_fit = ARIMAResults.load('app/arima_model.pkl')
except Exception as e:
    print(f"Error loading ARIMA model: {e}")
    model_fit = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/forecast', methods=['POST'])
def forecast():
    try:
        # Load the data (make sure 'retail-data.csv' exists)
        df = pd.read_csv("data/retail-data.csv")
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date')
        df.set_index('Date', inplace=True)
        y = df['Sales']

        # Split data into train and test sets (example: last 20% as test)
        train_size = int(len(y) * 0.8)
        train, test = y[:train_size], y[train_size:]

    except Exception as e:
        return f"Error loading or processing data: {e}"

    try:
        # Define how many steps ahead to forecast
        steps = int(request.form.get('steps'))

        # Forecast
        forecast = model_fit.forecast(steps=steps)

        # Generate future dates
        future_dates = pd.date_range(start=y.index[-1] + pd.Timedelta(days=1), periods=steps, freq='D')

        # Plot the forecast, actual sales, and test sales
        plt.figure(figsize=(14, 7))
        plt.plot(y.index, y, label='Actual Sales', color='blue')
        plt.plot(future_dates, forecast, label='Forecasted Sales(avg)', color='orange')
        plt.plot(test.index, test, label='forcast Sales', color='green')
        plt.xlabel('Date')
        plt.ylabel('Sales')
        plt.title('Sales Forecast')
        plt.legend()
        plt.grid(True)

        # Save the plot to a BytesIO object
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        # Render the forecast template with the plot
        return render_template('forecast.html', plot_url=plot_url)
    except Exception as e:
        return f"Error during forecasting or plotting: {e}"

if __name__ == '__main__':
    app.run(debug=True)
