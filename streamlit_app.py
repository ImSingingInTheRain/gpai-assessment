import streamlit as st
import pandas as pd
import io

# ---------------------------------------------
# Initialize answer dictionaries
# ---------------------------------------------
sub_mod_assessment = {}
pre_answers = {}
answers = {}
sys_risk_answers = {}

# ---------------------------------------------
# Title and Introduction
# ---------------------------------------------
st.title("General-Purpose AI Model Classification Tool")

st.info("""
**Important Notice**  
This tool assesses if your AI model qualifies as a General-Purpose AI (GPAI).  
**Automatically Excluded Models (examples):**  
- Rule-based systems  
- Small supervised classifiers (e.g., spam detection)  
- Single-purpose NLP or vision models  
- Specialized anomaly detection systems  
- Traditional statistical models  
- RPA systems.

Confirm your model is not in these categories before proceeding.
""")

# ---------------------------------------------
# Step 1: Automatic Exclusion Check
# ---------------------------------------------
st.header("Step 1: Automatic Exclusion Check")
auto_exclude = st.radio(
    "Does the above exclusion criterion clearly apply to your AI model?",
    ['Yes', 'No'],
    key="auto_exclude"
)
if auto_exclude == 'Yes':
    st.error("Your model is automatically excluded from GPAI assessment.")
    st.stop()

# ---------------------------------------------
# Step 2: Provider Determination
# ---------------------------------------------
st.header("Step 2: Provider Determination")
developed_internally = st.radio(
    "Was the model developed internally or procured from a third party?",
    ["Internally Developed", "Third Party"],
    key="provider_determination"
)

st.info("""
- **Internally Developed:** Continue to the assessment directly.
- **Third Party:** Additional evaluation of modifications is required.
""")

thirdparty_modified = "N/A"
if developed_internally == "Third Party":
    thirdparty_modified = st.radio(
        "Has the third-party model been modified in any way (e.g., retraining, architectural changes)?",
        ["Yes", "No"],
        key="thirdparty_modified"
    )
    if thirdparty_modified == "No":
        st.success("Unmodified third-party models are excluded from GPAI obligations.")
        st.stop()
    else:
        st.info("Third-party model modifications detected—continue assessment.")

# ---------------------------------------------
# Step 3: Pre-screening Questions
# ---------------------------------------------
st.header("Step 3: Pre-screening Questions")
pre_questions = {
    "params_below": (
        "Is the model's parameter count significantly below 1 billion?",
        "Models under 1 billion parameters generally lack significant generality."
    ),
    "trained_specialized": (
        "Was the model trained primarily on specialized, limited datasets?",
        "General-purpose AI typically relies on large, diverse training datasets."
    ),
    "single_task": (
        "Is the model effective only for a single, narrowly-defined task?",
        "GPAI models must competently address multiple distinct tasks."
    ),
    "adaptability": (
        "Is the model unable to adapt or be repurposed for different tasks?",
        "Adaptability (e.g., fine-tuning) is crucial for GPAI classification."
    )
}

for key, (question, guidance) in pre_questions.items():
    pre_answers[key] = st.radio(question, ["Yes", "No"], key=f"pre_{key}")
    st.markdown(f"<small>{guidance}</small>", unsafe_allow_html=True)

if (
    (pre_answers["params_below"] == "Yes" and pre_answers["trained_specialized"] == "Yes")
    or pre_answers["single_task"] == "Yes"
    or pre_answers["adaptability"] == "Yes"
):
    st.error("Pre-screening outcome: Model is eliminated from GPAI classification.")
    st.stop()

# ---------------------------------------------
# Step 3a: Substantial Modification Assessment using MCDA
# ---------------------------------------------
if developed_internally == "Third Party" and thirdparty_modified == "Yes":
    st.header("Step 3a: Substantial Modification Assessment")
    st.info("""
This framework evaluates modifications using a Multi-Criteria Decision Analysis (MCDA) approach.
For each subcriterion below, assign a score from 1 (very low impact) to 5 (very high impact).  
The overall score is computed as a weighted sum of the category averages:
    • Intended Purpose Change: 30%
    • Architectural/Algorithmic Changes: 25%
    • Data/Training Changes: 20%
    • Performance/Risk Impact: 15%
    • Future Deployment Change: 10%
An overall score > 3.5 indicates substantial modifications.
    """)

    # 1. Intended Purpose Change (30%)
    st.subheader("Intended Purpose Change (30%)")
    intended_purpose_subcriteria = {
         "intended_tasks": (
             "Intended Tasks & Integration:\n"
             "Does the modification change the description of intended tasks or affect the list of high-risk or restricted tasks (Annex XI 1.(a))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Minor change in task description.\n  5: Introduces a completely new use case with different stakeholder/regulatory implications."
         ),
         "acceptable_use": (
             "Acceptable Use Policy Consistency:\n"
             "Does the modification affect acceptable use policy elements (Annex XI 1.(b))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Some adjustments in policy.\n  5: Substantial policy revisions that alter permitted applications."
         ),
         "licensing": (
             "Licensing & Asset Release:\n"
             "Does the change alter the model’s licensing terms or the list of released assets (Annex XI 1.(f))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Minor modifications.\n  5: Changes that could affect downstream usage or legal compliance."
         )
    }
    intended_purpose_scores = {}
    for key, question in intended_purpose_subcriteria.items():
         intended_purpose_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"intended_{key}")
    intended_purpose_avg = sum(intended_purpose_scores.values()) / len(intended_purpose_scores)
    st.write("Intended Purpose Average Score:", round(intended_purpose_avg, 2))

    # 2. Architectural/Algorithmic Changes (25%)
    st.subheader("Architectural/Algorithmic Changes (25%)")
    architectural_subcriteria = {
         "model_architecture": (
             "Model Architecture and Parameter Changes:\n"
             "Does the modification change the overall architecture or parameter settings (Annex XI 1.(d))?\n"
             "Guidance:\n"
             "  1: Minor tweaks.\n  3: Moderate modifications.\n  5: Fundamental redesign."
         ),
         "design_training": (
             "Design Specifications & Training Process:\n"
             "Are there changes in design choices or training process steps (Annex XI 1 2.(b))?\n"
             "Guidance:\n"
             "  1: Negligible impact.\n  3: Moderate revisions.\n  5: Major revisions that could change how the model learns."
         ),
         "io_modalities": (
             "Input/Output Modalities:\n"
             "Has the modality, format, or limits of inputs/outputs changed (Annex XI 1.(e))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Some changes affecting data handling.\n  5: Significant alteration affecting inputs/outputs."
         )
    }
    architectural_scores = {}
    for key, question in architectural_subcriteria.items():
         architectural_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"arch_{key}")
    architectural_avg = sum(architectural_scores.values()) / len(architectural_scores)
    st.write("Architectural/Algorithmic Average Score:", round(architectural_avg, 2))

    # 3. Data/Training Changes (20%)
    st.subheader("Data/Training Changes (20%)")
    data_subcriteria = {
         "data_acquisition": (
             "Data Acquisition & Composition:\n"
             "Does the modification alter data sourcing (methods, time periods, source proportions) (Annex XI 1 2.(c))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Moderate change.\n  5: Substantial changes that could introduce bias."
         ),
         "data_processing": (
             "Data Processing & Quality:\n"
             "Are there modifications in data processing techniques (handling copyrighted, personal, or harmful data) (Annex XI 1 2.(c), Draft Document 17)?\n"
             "Guidance:\n"
             "  1: Minor adjustments.\n  3: Moderate changes.\n  5: Major processing changes with potential impacts on quality."
         ),
         "compute_resources": (
             "Computational Resources:\n"
             "Do training hardware, duration, or compute metrics change (Annex XI 1 2.(d))?\n"
             "Guidance:\n"
             "  1: Minor resource tweaks.\n  3: Moderate changes.\n  5: Major shifts affecting training scale or efficiency."
         ),
         "energy_consumption": (
             "Energy Consumption:\n"
             "Does the modification significantly change energy usage or emissions (Annex XI 1 2.(e))?\n"
             "Guidance:\n"
             "  1: Negligible impact.\n  3: Moderate change.\n  5: Significant impact on environmental cost."
         )
    }
    data_scores = {}
    for key, question in data_subcriteria.items():
         data_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"data_{key}")
    data_avg = sum(data_scores.values()) / len(data_scores)
    st.write("Data/Training Average Score:", round(data_avg, 2))

    # 4. Performance/Risk Impact (15%)
    st.subheader("Performance/Risk Impact (15%)")
    performance_subcriteria = {
         "quant_performance": (
             "Quantitative Performance Metrics:\n"
             "Does the modification result in measurable changes in accuracy, error rates, or other key metrics (Annex Article 53(1)(a))?\n"
             "Guidance:\n"
             "  1: No measurable impact.\n  3: Moderate change (e.g., 5-10% shift).\n  5: Significant performance shifts."
         ),
         "qual_risk": (
             "Qualitative Risk Assessment:\n"
             "Does the modification introduce new failure modes, vulnerabilities, or ethical concerns (Annex Article 53(1)(a))?\n"
             "Guidance:\n"
             "  1: No new risks.\n  3: Some new risks but manageable.\n  5: High risk or new critical vulnerabilities."
         ),
         "testing_results": (
             "Testing Process and Results:\n"
             "Are there significant changes in test outcomes or evaluation reports?\n"
             "Guidance:\n"
             "  1: Unchanged test results.\n  3: Moderate changes observed.\n  5: Substantial changes impacting reliability."
         )
    }
    performance_scores = {}
    for key, question in performance_subcriteria.items():
         performance_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"perf_{key}")
    performance_avg = sum(performance_scores.values()) / len(performance_scores)
    st.write("Performance/Risk Impact Average Score:", round(performance_avg, 2))

    # 5. Future Deployment Change (10%)
    st.subheader("Future Deployment Change (10%)")
    future_deployment_subcriteria = {
         "distribution_release": (
             "Distribution & Release:\n"
             "Are there changes in the model’s release date, distribution channels, or level of access (Annex XI 1.(c))?\n"
             "Guidance:\n"
             "  1: Unchanged.\n  3: Moderate changes.\n  5: Significant changes affecting market timing or user access."
         ),
         "external_dependencies": (
             "External Dependencies:\n"
             "Does the modification change how the model interacts with external hardware/software (Annex XII 1.(d) and 1.(e))?\n"
             "Guidance:\n"
             "  1: No change.\n  3: Some modifications.\n  5: Significant modifications requiring new dependencies."
         ),
         "integration_documentation": (
             "Integration Documentation:\n"
             "Are there revisions to the technical documentation guiding model integration (Annex XI 1 2.(a))?\n"
             "Guidance:\n"
             "  1: Minor updates.\n  3: Moderate changes.\n  5: Substantial changes affecting downstream implementation."
         )
    }
    future_deployment_scores = {}
    for key, question in future_deployment_subcriteria.items():
         future_deployment_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"future_{key}")
    future_deployment_avg = sum(future_deployment_scores.values()) / len(future_deployment_scores)
    st.write("Future Deployment Average Score:", round(future_deployment_avg, 2))

    # Calculate overall weighted score using defined weights
    overall_score = (0.30 * intended_purpose_avg +
                     0.25 * architectural_avg +
                     0.20 * data_avg +
                     0.15 * performance_avg +
                     0.10 * future_deployment_avg)
    st.write("**Overall Modification Score:**", round(overall_score, 2), "out of 5")

    # Interpretation: overall score > 3.5 indicates substantial modifications.
    if overall_score <= 3.5:
         st.success("Minor modifications only—no provider obligations apply.")
         st.stop()
    else:
         st.warning("Substantial modifications identified—continue to detailed assessment.")

    # Save the MCDA scores for audit purposes
    sub_mod_assessment["intended_purpose_avg"] = intended_purpose_avg
    sub_mod_assessment["architectural_avg"] = architectural_avg
    sub_mod_assessment["data_avg"] = data_avg
    sub_mod_assessment["performance_avg"] = performance_avg
    sub_mod_assessment["future_deployment_avg"] = future_deployment_avg
    sub_mod_assessment["overall_score"] = overall_score

# ---------------------------------------------
# Step 4: Detailed GPAI Assessment
# ---------------------------------------------
st.subheader("Step 4: Detailed GPAI Assessment")

score = 0

detailed_questions = {
    "params": (
        "Does the model have at least 1 billion parameters?",
        {"Yes": 2, "No": 0},
        "Models ≥1B parameters indicate significant generality (Recital 98)."
    ),
    "training": (
        "Was the model trained on large diverse datasets using self-supervision?",
        {"Yes": 2, "Partly": 1, "No": 0},
        "Generality arises from extensive data and self-supervised learning."
    ),
    "tasks": (
        "Does the model demonstrate competent performance in multiple distinct tasks?",
        {"Yes": 2, "Partly": 1, "No": 0},
        "Competence in multiple tasks characterizes GPAI."
    ),
    "generative": (
        "Can the model generate adaptable content across tasks/domains?",
        {"Yes": 2, "Partly": 1, "No": 0},
        "Generative flexibility aligns with GPAI."
    ),
    "modality": (
        "What data modality does the model handle?",
        {"Multi-modal": 2, "Single-flexible": 1, "Single-specialized": 0},
        "Multi-modality or flexible single-modality aligns with GPAI criteria."
    ),
    "integration": (
        "Can the model be readily integrated, fine-tuned, or prompt-engineered for new applications?",
        {"Yes": 2, "No": 0},
        "High adaptability supports GPAI classification."
    ),
    "use_cases": (
        "Are there multiple known or intended downstream use cases spanning different domains?",
        {"Yes": 2, "Partial": 1, "No": 0},
        "Broad downstream applicability supports GPAI."
    )
}

for key, (question, scoring, guidance) in detailed_questions.items():
    answers[key] = st.radio(question, list(scoring.keys()), key=f"detailed_{key}")
    st.markdown(f"<small>{guidance}</small>", unsafe_allow_html=True)
    score += scoring[answers[key]]

# Scoring-based classification for detailed assessment
if score >= 10:
    classification = "GPAI"
elif score >= 6:
    classification = st.radio(
        "Borderline outcome – classify this model as:",
        ["GPAI", "Not GPAI"],
        key="borderline"
    )
    manual_rationale = st.text_area("Provide rationale for this decision:", key="manual_rationale")
else:
    classification = "Not GPAI"

st.write("Final Classification:", classification)

# ---------------------------------------------
# Step 5: Systemic Risk Assessment (if GPAI)
# ---------------------------------------------
if classification == "GPAI":
    st.subheader("Step 5: Systemic Risk Assessment")

    sys_risk_questions = {
        "flops": "Does the model training involve ≥10^25 floating-point operations (FLOP)?",
        "state_of_art": "Is the model state-of-the-art or pushing state-of-the-art?",
        "scalability": "Does the model have significant reach or scalability?",
        "scaffolding": "Can the model significantly enable harmful applications through scaffolding?"
    }

    for key, question in sys_risk_questions.items():
        sys_risk_answers[key] = st.radio(question, ["Yes", "No"], key=f"sysrisk_{key}")

    # Determine systemic classification
    if sys_risk_answers["flops"] == "Yes" or sys_risk_answers["state_of_art"] == "Yes":
        systemic_classification = "GPAI with systemic risk"
    elif sys_risk_answers["scalability"] == "Yes" or sys_risk_answers["scaffolding"] == "Yes":
        st.warning("Borderline systemic risk – Further review recommended")
        final_decision = st.radio(
            "Final systemic risk decision:",
            ["GPAI with systemic risk", "GPAI without systemic risk"],
            key="final_sys_decision"
        )
        sys_rationale = st.text_area("Provide rationale:", key="sys_rationale")
        systemic_classification = final_decision
    else:
        systemic_classification = "GPAI without systemic risk"

    st.write("Systemic Risk Classification:", systemic_classification)

    # Obligations Visualization
    st.subheader("Applicable Obligations Under the AI Act")
    if systemic_classification == "GPAI with systemic risk":
        st.error(
            "The following obligations apply:\n"
            "- Provide technical documentation (Article 53(1)(a-b))\n"
            "- Public summary of training content (Article 53(1)(d))\n"
            "- Copyright compliance policy (Article 53(1)(c))\n"
            "- Systemic risk assessment and mitigation\n"
            "- Serious incident monitoring and reporting\n"
            "- Cybersecurity protection"
        )
    elif systemic_classification == "GPAI without systemic risk":
        st.success(
            "The following obligations apply:\n"
            "- Provide technical documentation (Article 53(1)(a-b))\n"
            "- Public summary of training content (Article 53(1)(d))\n"
            "- Copyright compliance policy (Article 53(1)(c))"
        )
    else:
        st.warning("No obligations apply because the final classification is 'Not GPAI with systemic risk'.")

# ---------------------------------------------
# Final Step: Model Details + CSV Download
# ---------------------------------------------
model_name = st.text_input("Model Name or Unique Identifier", key="model_name")
model_owner = st.text_input("Model Owner", key="model_owner")

# Gather all relevant answers
all_data = {
    "Model Name": model_name,
    "Model Owner": model_owner,
    "Final Classification": classification,
    "Systemic Risk Classification": systemic_classification if classification == "GPAI" else "N/A",
}

# Merge Step 2 answers (modification assessment)
for k, v in sub_mod_assessment.items():
    all_data[f"Step2_ModAssessment_{k}"] = v

# Merge Step 3 answers (pre-screening)
for k, v in pre_answers.items():
    all_data[f"Step3_PreScreen_{k}"] = v

# Merge Step 4 answers (detailed assessment)
for k, v in answers.items():
    all_data[f"Step4_Detailed_{k}"] = v

# Merge Step 5 answers (systemic risk assessment)
for k, v in sys_risk_answers.items():
    all_data[f"Step5_SysRisk_{k}"] = v

# Merge textual rationales for audit trails (if provided)
all_data["Step4_Manual_Rationale"] = st.session_state.get("manual_rationale", "")
all_data["Step5_SysRationale"] = st.session_state.get("sys_rationale", "")

# Download button for CSV
if st.button("Download CSV Summary"):
    buffer = io.StringIO()
    df = pd.DataFrame([all_data])  # single-row dataframe
    df.to_csv(buffer, index=False)

    st.download_button(
        label="Click to Download CSV",
        data=buffer.getvalue(),
        file_name=f"{model_name}_assessment.csv",
        mime="text/csv"
    )