from math import ceil
from flask import Flask, render_template, request

app = Flask(__name__)

QUESTIONNAIRE = [
    {
        "name": "km_auto",
        "label": "Quanti chilometri guidi in auto ogni settimana?",
        "unit": "km",
        "placeholder": "Es. 200",
        "factor": 0.12,
        "description": "Emissioni medie auto: 0,12 kg CO2 per km."
    },
    {
        "name": "kwh_elettricita",
        "label": "Quanti kWh consumi in elettricità ogni mese?",
        "unit": "kWh",
        "placeholder": "Es. 250",
        "factor": 0.5,
        "description": "Emissioni medie elettricità: 0,5 kg CO2 per kWh."
    },
    {
        "name": "m3_metano",
        "label": "Quanti metri cubi di gas naturale consumi in casa ogni mese?",
        "unit": "m³",
        "placeholder": "Es. 100",
        "factor": 2.0,
        "description": "Emissioni medie gas naturale: 2 kg CO2 per m³."
    },
    {
        "name": "voli_brevi",
        "label": "Quanti voli brevi (fino a 3 ore) fai all'anno?",
        "unit": "volo/i",
        "placeholder": "Es. 2",
        "factor": 150,
        "description": "Un volo breve genera circa 150 kg CO2."
    },
    {
        "name": "voli_lunghi",
        "label": "Quanti voli lunghi (oltre 3 ore) fai all'anno?",
        "unit": "volo/i",
        "placeholder": "Es. 1",
        "factor": 600,
        "description": "Un volo lungo genera circa 600 kg CO2."
    }
]

TREE_CO2_ABSORPTION_PER_YEAR = 22.0


def parse_float(value: str) -> float:
    try:
        return float(value.replace(",", "."))
    except (ValueError, AttributeError):
        return 0.0


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    errors = []

    if request.method == "POST":
        answers = {}
        total_co2 = 0.0
        breakdown = []

        for question in QUESTIONNAIRE:
            raw_value = request.form.get(question["name"], "0")
            value = parse_float(raw_value)

            if value < 0:
                errors.append(f"Il valore per '{question['label']}' deve essere positivo.")
                value = 0.0

            if question["name"] == "km_auto":
                annual_value = value * 52
            elif question["name"] in ["kwh_elettricita", "m3_metano"]:
                annual_value = value * 12
            else:
                annual_value = value

            emission = annual_value * question["factor"]
            total_co2 += emission
            breakdown.append({
                "label": question["label"],
                "value": value,
                "unit": question["unit"],
                "emission": emission,
                "description": question["description"]
            })

            answers[question["name"]] = raw_value

        if not errors:
            trees_needed = ceil(total_co2 / TREE_CO2_ABSORPTION_PER_YEAR)
            result = {
                "total_co2": total_co2,
                "trees_needed": trees_needed,
                "breakdown": breakdown
            }

        return render_template("result.html", result=result, errors=errors, answers=answers)

    return render_template("index.html", questionnaire=QUESTIONNAIRE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
