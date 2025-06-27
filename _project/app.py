
from flask import Flask, render_template, request, send_file
from services.saju_engine.analyze import analyze_saju
import io
import matplotlib.pyplot as plt
from fpdf import FPDF

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    birthdate = request.form.get("birthdate")
    gender = request.form.get("gender")
    time_str = request.form.get("time")

    result = analyze_saju(birthdate, gender, time_str)
    return render_template("result.html", result=result)

@app.route("/download_pdf", methods=["POST"])
def download_pdf():
    birthdate = request.form.get("birthdate")
    gender = request.form.get("gender")
    time_str = request.form.get("time")
    result = analyze_saju(birthdate, gender, time_str)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="사주 분석 리포트", ln=True, align="C")

    for key in result:
        value = result[key]
        if isinstance(value, dict):
            pdf.cell(200, 10, txt=f"{key}:", ln=True)
            for k, v in value.items():
                pdf.cell(200, 10, txt=f"  {k}: {v}", ln=True)
        elif isinstance(value, list):
            pdf.cell(200, 10, txt=f"{key}:", ln=True)
            for item in value:
                pdf.cell(200, 10, txt=f"  {item}", ln=True)
        else:
            pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    return send_file(pdf_output, as_attachment=True, download_name="saju_report.pdf", mimetype="application/pdf")

@app.route("/ohaeng_chart.png")
def ohaeng_chart():
    birthdate = request.args.get("birthdate")
    gender = request.args.get("gender")
    time_str = request.args.get("time")
    result = analyze_saju(birthdate, gender, time_str)

    ohaeng = result["ohaeng"]
    labels = list(ohaeng.keys())
    values = list(ohaeng.values())

    fig, ax = plt.subplots()
    ax.bar(labels, values)
    ax.set_title("오행 분포")
    ax.set_ylabel("비중")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    return send_file(img, mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True)
