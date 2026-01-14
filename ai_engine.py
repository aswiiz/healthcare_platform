def predict_disease(v, s):
    risk = []

    if int(v["bp"]) > 140:
        risk.append("High Blood Pressure")
    if int(v["sugar"]) > 160:
        risk.append("Diabetes Risk")
    if int(v["oxygen"]) < 92:
        risk.append("Breathing Issue")
    if int(v["cholesterol"]) > 240:
        risk.append("Heart Disease Risk")
    if "pain" in s.lower() or "tired" in s.lower():
        risk.append("General Health Risk")

    if not risk:
        return "No major health risks detected"

    return ", ".join(risk)
