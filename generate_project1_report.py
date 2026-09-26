from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)

BASE = Path(".")
OUT = BASE / "processed_data" / "Project1_Final_Baseline_Report.pdf"
FIG = BASE / "processed_data" / "final_figures"

doc = SimpleDocTemplate(
    str(OUT),
    pagesize=A4,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45,
)

styles = getSampleStyleSheet()

title = ParagraphStyle(
    "TitleCustom",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=22,
    leading=27,
    spaceAfter=18,
)

subtitle = ParagraphStyle(
    "SubtitleCustom",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=12,
    leading=17,
    spaceAfter=20,
)

h1 = ParagraphStyle(
    "H1Custom",
    parent=styles["Heading1"],
    fontSize=16,
    leading=20,
    spaceBefore=12,
    spaceAfter=10,
)

h2 = ParagraphStyle(
    "H2Custom",
    parent=styles["Heading2"],
    fontSize=13,
    leading=17,
    spaceBefore=10,
    spaceAfter=7,
)

body = ParagraphStyle(
    "BodyCustom",
    parent=styles["BodyText"],
    fontSize=9.5,
    leading=14,
    spaceAfter=7,
)

small = ParagraphStyle(
    "SmallCustom",
    parent=styles["BodyText"],
    fontSize=8,
    leading=11,
)

code = ParagraphStyle(
    "CodeCustom",
    parent=styles["Code"],
    fontSize=7.5,
    leading=10,
    leftIndent=10,
)

story = []

# ---------------------------------------------------------
# COVER
# ---------------------------------------------------------

story.append(Spacer(1, 0.8 * inch))
story.append(Paragraph(
    "SELF-SUPERVISED LEARNING FOR ZERO-DAY UAV ATTACK DETECTION",
    title
))
story.append(Paragraph(
    "Project 1 — Final Baseline Implementation and Evaluation Report",
    subtitle
))
story.append(Spacer(1, 0.3 * inch))

cover_data = [
    ["Platform", "PX4 SITL + Gazebo X500"],
    ["Data Source", "PX4 ULog flight telemetry"],
    ["Normal Flights", "3"],
    ["Normal Windows", "476"],
    ["Original Abnormal Windows", "48"],
    ["Window Size", "20 samples"],
    ["Window Step", "5 samples"],
    ["Telemetry Features", "21"],
    ["Transformer Embedding", "128 dimensions"],
    ["Controlled Attack", "GPS WRONG failure injection"],
]

t = Table(cover_data, colWidths=[2.0*inch, 4.1*inch])
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("TOPPADDING", (0,0), (-1,-1), 7),
    ("BOTTOMPADDING", (0,0), (-1,-1), 7),
]))
story.append(t)
story.append(Spacer(1, 0.4 * inch))
story.append(Paragraph(
    "Purpose: establish and evaluate a self-supervised UAV telemetry "
    "anomaly-detection baseline using normal flight data and controlled "
    "PX4 SITL experiments.",
    body
))
story.append(PageBreak())

# ---------------------------------------------------------
# 1. OBJECTIVE
# ---------------------------------------------------------

story.append(Paragraph("1. Project Objective", h1))
story.append(Paragraph(
    "The objective of Project 1 is to investigate whether a UAV telemetry "
    "representation learned from normal flight behavior can be used to "
    "identify previously unseen abnormal behavior. The implementation uses "
    "PX4 Software-In-The-Loop (SITL), Gazebo simulation, telemetry "
    "preprocessing, time-window construction, an autoencoder baseline, and "
    "a Transformer encoder trained using self-supervised contrastive learning.",
    body
))
story.append(Paragraph(
    "The project is designed as a research baseline. The results demonstrate "
    "the behavior of the implemented methods on the collected simulation "
    "datasets; they should not be interpreted as proof of universal zero-day "
    "attack detection.",
    body
))

# ---------------------------------------------------------
# 2. SYSTEM ARCHITECTURE
# ---------------------------------------------------------

story.append(Paragraph("2. System Architecture", h1))
architecture = (
    "PX4 SITL → Gazebo X500 → MAVSDK / PX4 ULog → Telemetry Extraction "
    "→ Preprocessing → Normalization → 20-sample Windows → "
    "Autoencoder Baseline + Transformer Contrastive Encoder → "
    "128-D Embeddings → Anomaly Detection → Evaluation"
)
story.append(Paragraph(architecture, body))

story.append(Paragraph("Main telemetry features", h2))
features = (
    "Position: x, y, z; velocity: vx, vy, vz; acceleration: ax, ay, az; "
    "attitude: roll, pitch, yaw; angular velocity: angular_x, angular_y, "
    "angular_z; battery: voltage_v, remaining; actuator outputs: motor_1 "
    "through motor_4."
)
story.append(Paragraph(features, body))

# ---------------------------------------------------------
# 3. ENVIRONMENT
# ---------------------------------------------------------

story.append(Paragraph("3. Experimental Environment", h1))
env = [
    ["Component", "Configuration"],
    ["Operating system", "Ubuntu 24.04.5 LTS in WSL2"],
    ["Simulator", "PX4 SITL"],
    ["Vehicle", "Gazebo X500"],
    ["Gazebo", "Gazebo Harmonic 8.15.0"],
    ["Python", "3.12.3"],
    ["MAVSDK", "3.17.2"],
    ["NumPy", "2.5.3"],
    ["scikit-learn", "1.9.1"],
    ["TensorFlow", "Installed in project virtual environment"],
]
t = Table(env, colWidths=[2.0*inch, 4.1*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t)

# ---------------------------------------------------------
# 4. DATA COLLECTION
# ---------------------------------------------------------

story.append(Paragraph("4. Normal Flight Data Collection", h1))
story.append(Paragraph(
    "Three normal SITL flights were generated using MAVSDK. Each flight "
    "performed takeoff, hover, directional movement, additional hovering, "
    "and landing. PX4 ULog files were extracted from the SITL log directory.",
    body
))

normal_flights = [
    ["Flight", "Processed Samples", "Label"],
    ["01", "803", "Normal"],
    ["02", "803", "Normal"],
    ["03", "945", "Normal"],
    ["Total", "2551", "Normal"],
]
t = Table(normal_flights, colWidths=[1.2*inch, 2.0*inch, 2.5*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ("FONTSIZE", (0,0), (-1,-1), 9),
    ("TOPPADDING", (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
]))
story.append(t)

# ---------------------------------------------------------
# 5. PREPROCESSING
# ---------------------------------------------------------

story.append(Paragraph("5. Data Preprocessing", h1))
story.append(Paragraph(
    "PX4 ULog topics were extracted and aligned to a common 10 Hz timeline. "
    "Quaternion attitude data were converted to roll, pitch, and yaw. "
    "Telemetry streams were merged using nearest timestamps with a 0.15 s "
    "tolerance, followed by interpolation and forward/backward filling.",
    body
))
story.append(Paragraph(
    "The constant current_a feature was removed during dataset combination. "
    "The final machine-learning input contains 21 telemetry features. "
    "Normalization used StandardScaler fitted only on normal data.",
    body
))

story.append(Paragraph("Window construction", h2))
story.append(Paragraph(
    "Window size = 20 samples; step = 5 samples. At 10 Hz, each window "
    "represents approximately 2 seconds of telemetry and consecutive windows "
    "are shifted by approximately 0.5 seconds.",
    body
))

window_data = [
    ["Dataset", "Windows", "Normal", "Abnormal"],
    ["Original evaluation dataset", "524", "476", "48"],
    ["Attack 01 dataset", "1983", "1729", "254"],
]
t = Table(window_data, colWidths=[2.5*inch, 1.1*inch, 1.1*inch, 1.1*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
]))
story.append(t)

# ---------------------------------------------------------
# 6. AUTOENCODER
# ---------------------------------------------------------

story.append(Paragraph("6. Autoencoder Baseline", h1))
story.append(Paragraph(
    "A reconstruction-based autoencoder was trained using only normal "
    "windows. The network flattens the 20×21 input and passes it through "
    "Dense layers of 128, 64, and 32 units before reconstructing the "
    "original 20×21 telemetry window.",
    body
))
story.append(Paragraph(
    "Training used Adam with learning rate 0.001, mean squared error loss, "
    "50 epochs, batch size 32, and a 20% validation split. The anomaly "
    "threshold was calculated from the normal reconstruction errors using "
    "mean + 3 standard deviations.",
    body
))

ae_table = [
    ["Metric", "Result"],
    ["Training windows", "476 normal"],
    ["Final training loss", "0.041834"],
    ["Final validation loss", "0.205007"],
    ["Threshold", "0.536384"],
    ["Accuracy", "95.80%"],
    ["Precision", "68.57%"],
    ["Recall", "100.00%"],
    ["F1", "81.36%"],
    ["TN / FP / FN / TP", "454 / 22 / 0 / 48"],
]
t = Table(ae_table, colWidths=[2.5*inch, 3.2*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
]))
story.append(t)

story.append(Spacer(1, 10))
story.append(Image(str(FIG/"02_autoencoder_reconstruction_error.png"), width=6.5*inch, height=3.9*inch))
story.append(Paragraph(
    "Figure 1. Autoencoder reconstruction-error distribution.",
    small
))

story.append(PageBreak())

# ---------------------------------------------------------
# 7. TRANSFORMER
# ---------------------------------------------------------

story.append(Paragraph("7. Self-Supervised Transformer", h1))
story.append(Paragraph(
    "The Transformer receives a 20×21 telemetry window. A Dense projection "
    "maps the 21 features into a 128-dimensional representation and a "
    "learned positional embedding is added. Two Transformer blocks use "
    "4-head self-attention and a 256-unit feed-forward network.",
    body
))
story.append(Paragraph(
    "The final GlobalAveragePooling1D layer is followed by a 128-dimensional "
    "embedding layer. The resulting encoder contains 286,848 trainable "
    "parameters.",
    body
))

story.append(Paragraph("Contrastive learning", h2))
story.append(Paragraph(
    "Two augmented views were generated for every normal window. The "
    "augmentations consisted of small Gaussian noise and small per-feature "
    "scaling. The encoder was trained with a symmetric NT-Xent / InfoNCE-style "
    "contrastive objective using temperature 0.1, Adam learning rate 0.0005, "
    "batch size 32, and 50 epochs.",
    body
))
story.append(Paragraph(
    "The final contrastive loss was approximately 0.0459. The trained encoder "
    "was saved as uav_transformer_encoder.keras.",
    body
))

# ---------------------------------------------------------
# 8. DETECTION METHODS
# ---------------------------------------------------------

story.append(Paragraph("8. Transformer Anomaly Detection Methods", h1))
story.append(Paragraph(
    "The learned 128-dimensional embeddings were evaluated using several "
    "distance or similarity-based approaches. The normal embeddings were "
    "used as the reference distribution.",
    body
))

methods = [
    ["Method", "Description"],
    ["Euclidean", "Distance from normal embedding centroid."],
    ["Standard Mahalanobis", "Covariance-aware distance using normal embeddings."],
    ["Robust Mahalanobis", "MinCovDet-based robust covariance reference."],
    ["Cosine", "1 − cosine similarity to normal embedding centroid."],
]
t = Table(methods, colWidths=[1.8*inch, 4.3*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
]))
story.append(t)

story.append(Spacer(1, 10))
story.append(Image(str(FIG/"03_transformer_mahalanobis_distribution.png"), width=6.5*inch, height=3.9*inch))
story.append(Paragraph(
    "Figure 2. Standard Mahalanobis distance distribution.",
    small
))

# ---------------------------------------------------------
# 9. FINAL BASELINE RESULTS
# ---------------------------------------------------------

story.append(Paragraph("9. Final Baseline Results", h1))
story.append(Paragraph(
    "The following results were obtained on the 524-window original "
    "evaluation dataset containing 476 normal and 48 abnormal windows.",
    body
))

results = [
    ["Method", "Accuracy", "Precision", "Recall", "F1"],
    ["Autoencoder", "95.80%", "68.57%", "100.00%", "81.36%"],
    ["Transformer + Euclidean", "90.84%", "0%", "0%", "0%"],
    ["Transformer + Standard Mahalanobis", "98.09%", "91.30%", "87.50%", "89.36%"],
    ["Transformer + Robust Mahalanobis", "89.12%", "0%", "0%", "0%"],
    ["Transformer + Cosine", "88.93%", "36.84%", "29.17%", "32.56%"],
]
t = Table(results, colWidths=[2.55*inch, .85*inch, .85*inch, .85*inch, .85*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 7.5),
    ("ALIGN", (1,0), (-1,-1), "CENTER"),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
]))
story.append(t)

story.append(Spacer(1, 10))
story.append(Image(str(FIG/"01_model_performance_comparison.png"), width=6.5*inch, height=3.55*inch))
story.append(Paragraph(
    "Figure 3. Experimental comparison of baseline detection methods.",
    small
))

story.append(PageBreak())

# ---------------------------------------------------------
# 10. CONFUSION MATRICES
# ---------------------------------------------------------

story.append(Paragraph("10. Confusion Matrices", h1))
story.append(Paragraph(
    "The standard Transformer + Mahalanobis detector produced 472 true "
    "normal classifications, 4 false positives, 6 false negatives, and "
    "42 true abnormal classifications on the original evaluation dataset.",
    body
))
story.append(Image(str(FIG/"04_transformer_confusion_matrix.png"), width=4.8*inch, height=4.0*inch))
story.append(Paragraph(
    "Figure 4. Transformer + Standard Mahalanobis confusion matrix.",
    small
))
story.append(Spacer(1, 10))
story.append(Image(str(FIG/"05_autoencoder_confusion_matrix.png"), width=4.8*inch, height=4.0*inch))
story.append(Paragraph(
    "Figure 5. Autoencoder confusion matrix.",
    small
))

# ---------------------------------------------------------
# 11. ATTACK 01
# ---------------------------------------------------------

story.append(PageBreak())
story.append(Paragraph("11. Controlled Attack 01 — GPS WRONG Failure Injection", h1))
story.append(Paragraph(
    "A controlled PX4 SITL GPS failure-injection experiment was conducted "
    "using the MAVSDK failure API. PX4's GPS WRONG failure mode was enabled "
    "for approximately 10 seconds and then restored. This experiment is "
    "described as a controlled GPS anomaly/failure-injection scenario; it is "
    "not equivalent to a real-world GPS receiver spoofing attack.",
    body
))
story.append(Paragraph(
    "The experiment generated a 79-second ULog. GPS-related topics contained "
    "2,409 samples. The labeled attack interval was approximately 37.048 s "
    "to 47.048 s, corresponding to approximately 10 seconds of commanded "
    "failure injection.",
    body
))

attack_data = [
    ["Item", "Result"],
    ["Attack type", "PX4 GPS WRONG failure injection"],
    ["Attack duration", "≈10.0 seconds"],
    ["Attack raw telemetry rows", "1,250"],
    ["Attack windows", "254"],
    ["Attack dataset windows", "1,983 total"],
    ["Normal windows", "1,729"],
]
t = Table(attack_data, colWidths=[2.6*inch, 3.5*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
]))
story.append(t)

story.append(Spacer(1, 10))
story.append(Image(str(FIG/"06_attack01_detection_timeline.png"), width=6.5*inch, height=3.7*inch))
story.append(Paragraph(
    "Figure 6. Transformer Mahalanobis distance during controlled Attack 01.",
    small
))

story.append(Paragraph("Attack 01 baseline evaluation", h2))
attack_results = [
    ["Metric", "Result"],
    ["Accuracy", "54.92%"],
    ["Precision", "13.96%"],
    ["Recall", "48.82%"],
    ["F1", "21.72%"],
    ["TN / FP / FN / TP", "965 / 764 / 130 / 124"],
]
t = Table(attack_results, colWidths=[2.5*inch, 3.2*inch], repeatRows=1)
t.setStyle(TableStyle([
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
]))
story.append(t)

# ---------------------------------------------------------
# 12. INTERPRETATION
# ---------------------------------------------------------

story.append(Paragraph("12. Experimental Findings", h1))
story.append(Paragraph(
    "The autoencoder successfully reconstructed normal telemetry and "
    "produced very large reconstruction errors for the original high-speed "
    "abnormal event. Its recall on that evaluation set was 100%, although "
    "22 normal windows were also classified as anomalous.",
    body
))
story.append(Paragraph(
    "The self-supervised Transformer produced 128-dimensional telemetry "
    "representations. Among the tested distance methods, standard "
    "Mahalanobis distance provided the strongest measured result on the "
    "original 524-window evaluation set, with 98.09% accuracy and an F1 "
    "score of 89.36%.",
    body
))
story.append(Paragraph(
    "The robust Mahalanobis and cosine experiments did not improve the "
    "measured baseline performance. Their results are retained as ablation "
    "experiments to document the behavior of alternative scoring methods.",
    body
))
story.append(Paragraph(
    "Attack 01 produced a substantial performance reduction when the "
    "detector trained from the normal reference was evaluated on the "
    "separately generated controlled GPS failure-injection dataset. This "
    "demonstrates that performance on one abnormal behavior should not be "
    "interpreted as guaranteed zero-day generalization to every attack type.",
    body
))

# ---------------------------------------------------------
# 13. LIMITATIONS
# ---------------------------------------------------------

story.append(Paragraph("13. Limitations", h1))
limitations = [
    "The experiments were performed in PX4 SITL/Gazebo rather than on a physical UAV.",
    "The original abnormal dataset is a high-speed/abnormal movement event and is not a confirmed cyberattack.",
    "Attack 01 is a controlled PX4 GPS failure-injection experiment and not a real-world GPS spoofing measurement.",
    "The dataset is relatively small and contains only three normal flights for the baseline reference.",
    "The reported thresholds were derived from the available normal reference data.",
    "The current Transformer is an encoder trained with self-supervised contrastive learning; further work is required to establish broader zero-day generalization."
]
for item in limitations:
    story.append(Paragraph("• " + item, body))

# ---------------------------------------------------------
# 14. FUTURE WORK
# ---------------------------------------------------------

story.append(Paragraph("14. Future Work", h1))
future = [
    "Generate multiple controlled UAV attack/failure scenarios in PX4 SITL.",
    "Evaluate whether attacks not represented during self-supervised training can be detected.",
    "Increase the number and diversity of normal flight trajectories.",
    "Investigate temporal contrastive augmentations and sequence-level objectives.",
    "Evaluate threshold calibration using a dedicated validation set.",
    "Compare against additional sequence anomaly-detection baselines.",
    "Test the trained encoder and detector on independent flight sessions.",
    "Investigate deployment on resource-constrained UAV/edge hardware."
]
for item in future:
    story.append(Paragraph("• " + item, body))

# ---------------------------------------------------------
# 15. COMMAND SUMMARY
# ---------------------------------------------------------

story.append(PageBreak())
story.append(Paragraph("15. Core Implementation Command Summary", h1))
commands = [
    "git clone https://github.com/PX4/PX4-Autopilot.git --recursive",
    "cd ~/PX4-Autopilot",
    "bash ./Tools/setup/ubuntu.sh",
    "make px4_sitl gz_x500",
    "cd ~/uav_project1",
    "source .venv/bin/activate",
    "python connect_test.py",
    "python telemetry_test.py",
    "python arm_test.py",
    "python takeoff_test.py",
    "python normal_flight.py",
    "python preprocess_flight.py 01",
    "python preprocess_flight.py 02",
    "python preprocess_flight.py 03",
    "python combine_normal_flights.py",
    "python combine_labeled_dataset.py",
    "python normalize_dataset.py",
    "python create_windows.py",
    "python train_autoencoder.py",
    "python evaluate_autoencoder.py",
    "python transformer_model.py",
    "python create_contrastive_views.py",
    "python train_transformer_contrastive.py",
    "python test_gps_failure.py",
    "python extract_attack01.py",
    "python combine_attack01...",
    "python evaluate_attack01...",
]
for cmd in commands:
    story.append(Paragraph(cmd, code))

story.append(Paragraph(
    "Note: the command summary above records the principal implementation "
    "commands. The complete terminal history remains the authoritative "
    "record for exact one-line experimental commands used during development.",
    body
))

# ---------------------------------------------------------
# 16. FILES
# ---------------------------------------------------------

story.append(Paragraph("16. Key Project Files", h1))
file_list = [
    "processed_data/normal_flights.csv",
    "processed_data/uav_labeled_dataset.csv",
    "processed_data/uav_normalized.csv",
    "processed_data/uav_windows_ml.npz",
    "processed_data/uav_autoencoder.keras",
    "processed_data/autoencoder_results.csv",
    "processed_data/uav_transformer_encoder.keras",
    "processed_data/all_transformer_embeddings.npz",
    "processed_data/transformer_mahalanobis_distances.npz",
    "processed_data/project1_baseline_results_summary.csv",
    "data_attack01/17_45_34.ulg",
    "data_attack01/attack01_labeled.csv",
    "data_attack01/attack01_windows_ml.npz",
    "data_attack01/attack01_baseline_results.csv",
    "data_attack01/attack01_transformer_embeddings.npz",
    "data_attack01/attack01_transformer_mahalanobis.npz",
]
for f in file_list:
    story.append(Paragraph("• " + f, body))

# ---------------------------------------------------------
# CONCLUSION
# ---------------------------------------------------------

story.append(Paragraph("17. Conclusion", h1))
story.append(Paragraph(
    "Project 1 establishes a complete experimental pipeline from PX4 SITL "
    "flight generation through telemetry preprocessing, self-supervised "
    "Transformer representation learning, anomaly scoring, and controlled "
    "attack evaluation. The strongest measured baseline on the original "
    "evaluation dataset was the Transformer with standard Mahalanobis "
    "distance. The separate GPS failure-injection experiment also revealed "
    "a significant generalization challenge, providing a concrete direction "
    "for the next stage of the research.",
    body
))

story.append(Spacer(1, 20))
story.append(Paragraph(
    "END OF PROJECT 1 BASELINE REPORT",
    ParagraphStyle(
        "End",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=11,
        leading=15,
    )
))

doc.build(story)

print("FINAL PDF GENERATED")
print("Output:", OUT)
print("Size: %.2f MB" % (OUT.stat().st_size / (1024*1024)))
