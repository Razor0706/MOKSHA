import numpy as np
from sklearn.linear_model import LogisticRegression


def build_lipid_training_dataset():
    total_cholesterol_values = [145, 160, 175, 190, 199, 205, 215, 225, 235, 240, 255, 275, 300, 330, 365]
    ldl_values = [65, 80, 95, 110, 125, 130, 140, 150, 159, 160, 175, 190, 210, 235]

    samples = []
    labels = []
    for cholesterol in total_cholesterol_values:
        for ldl in ldl_values:
            if cholesterol >= 240 or ldl >= 160:
                label = 2
            elif cholesterol >= 200 or ldl >= 130:
                label = 1
            else:
                label = 0

            samples.append([cholesterol, ldl])
            labels.append(label)

    boundary_examples = [
        ([198, 128], 0),
        ([200, 126], 1),
        ([208, 132], 1),
        ([235, 158], 1),
        ([241, 120], 2),
        ([188, 161], 2),
        ([260, 145], 2),
        ([220, 170], 2),
    ]
    for sample, label in boundary_examples:
        samples.append(sample)
        labels.append(label)

    return np.array(samples), np.array(labels)


def train_lipid_model():
    x_train, y_train = build_lipid_training_dataset()
    trained_model = LogisticRegression(max_iter=1000, class_weight="balanced")
    trained_model.fit(x_train, y_train)
    return trained_model


MODEL = train_lipid_model()


def predict_lipid_risk(cholesterol, ldl):
    if cholesterol is None or ldl is None:
        return "unknown", None

    prediction = int(MODEL.predict([[cholesterol, ldl]])[0])
    probabilities = MODEL.predict_proba([[cholesterol, ldl]])[0]
    confidence = round(float(np.max(probabilities)) * 100, 1)
    return {0: "low", 1: "moderate", 2: "high"}[prediction], confidence
