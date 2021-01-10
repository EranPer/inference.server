from flask import Flask
from flask import request
from joblib import dump, load
import json
import os

app = Flask(__name__)
model = load('life_expectancy_model.joblib')

features = ['Status', 'infant_deaths', 'percentage_expenditure', 'Hepatitis_B', \
           'Measles', 'BMI', 'Polio', 'HIV/AIDS', 'Population', \
           'thinness_1-19_years']


@app.route('/')
def index():
    html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Eran's website</title>
            </head>
            <body>
            <h2>
                Welcome to life expectancy prediction model<br>
                <a href="https://www.kaggle.com/kumarajarshi/life-expectancy-who">Kaggle's dataset</a>
            </h2>
            
            <form action="/predict_single_ui">
            '''
    html += get_features_table()
    html += '''
        <input type="submit" value="Submit">
        </form>
        
        <p>Click the "Submit" button when finished.</p>
        <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ">Premium content</a>
        
        </body>
        </html>
        '''
    return html


@app.route("/predict_single")
def predict_single():
    dict_for_prediction = request.args.to_dict(flat=False)
    if len(dict_for_prediction) == len(features):
        return 'The prediction for ' + str(dict_for_prediction) + ' is ' + str(get_prediction(dict_for_prediction))
    return 'Please go back and check you put values for all of the features'


@app.route("/predict_single_ui")
def predict_single_ui():
    dict_for_prediction = request.args.to_dict(flat=False)
    if len(dict_for_prediction) == len(features) and not [''] in list(dict_for_prediction.values()):
        html = '''
                <!DOCTYPE html>
                    <html>
                    <head>
                    <style>
                    table {
                      font-family: arial, sans-serif;
                      border-collapse: collapse;
                      width: 100%;
                    }

                    td, th {
                      border: 1px solid #dddddd;
                      text-align: left;
                      padding: 8px;
                    }

                    tr:nth-child(even) {
                      background-color: #dddddd;
                    }
                    </style>
                    </head>
                    <body>

                    <h2>Life expectancy prediction table</h2>

                    <table>
                      <tr>
                '''
        for feature in features:
            html += '<th>'
            html += feature
            html += '</th>'
        html += '<th>prediction</th>'
        html += '</tr><tr>'
        for item in dict_for_prediction.items():
            html += '<td>'
            html += str(item[1][0])
            html += '</td>'
        html += '<td>'
        html += str(round(get_prediction(dict_for_prediction)[0], 2))
        html += '</td>'
        html += '''
                </tr></table>

                </body>
                </html>
                '''
        return html
        # return 'The prediction for ' + str(dict_for_prediction) + ' is ' + str(get_prediction(dict_for_prediction))
    return 'Please go back and check you put values for all of the features'


@app.route("/json", methods=["POST"])
def multiple_predictions():
    # Validate the request body contains JSON
    if request.is_json:
        req = request.get_json()

        predictions = get_predictions_json(req)
        pred_list = []
        for pred in predictions:
            pred_list.append(pred[0])
        json_pred = json.dumps(pred_list)

        return json_pred, 200

    else:
        return "Request was not JSON", 400


def get_predictions_json(req):
    predictions = []
    for r in req:
        predictions.append(get_prediction(r))
    return predictions


def get_features_table():
    html = '''
            <table style="width:100%">
            <tr>
            '''
    for feature in features:
        html += '<th><label for="'
        html += feature
        html += '">'
        if feature == 'Statues':
            html += 'Status (1 - Developed; 0 - Developing)'
        else:
            html += feature
        html += '</label></th>'
    html += '</tr><tr>'

    for feature in features:
        html += '<th><input type="text" id="'
        html += feature
        html += '" name="'
        html += feature
        html += '" ></th>'
    html += '</tr></table><br>'

    return html


def get_prediction(dict_for_prediction):
    list_to_predict = []
    for k, v in dict_for_prediction.items():
        if isinstance(v, list):
            list_to_predict.append(float(v[0]))
        else:
            list_to_predict.append(float(v))
    return model.predict([list_to_predict])


def main():
    app.run()


if __name__ == '__main__':
    port = os.environ.get('PORT')

    if port:
        app.run(host='0.0.0.0', port=int(port))
    else:
        app.run()
