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
**Important Notice:**  
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
This assessment framework evaluates modifications using a Multi-Criteria Decision Analysis (MCDA) approach.  
For each subcriterion, rate the change on a scale of 1 (minimal change) to 5 (significant change).  
The overall score is computed as the weighted sum of the average scores of each category.  
A higher overall score indicates more substantial modifications. An overall score > 3.5 suggests substantial modifications.
    """)

    # 1. Intended Purpose Change (30%)
    st.subheader("Intended Purpose Change (30%)")
    intended_purpose_subcriteria = {
         "new_use_case": (
             "New Use Case Identification: Does the modification introduce a new use case not previously envisioned?\n"
             "Guidance:\n"
             "- 1: No new use case introduced; the application remains identical.\n"
             "- 3: Minor deviation or extension of the existing use case.\n"
             "- 5: A completely new and distinct use case is introduced."
         ),
         "stakeholder_variation": (
             "Stakeholder Variation: Does the modification involve different stakeholders (e.g., new user groups or regulators)?\n"
             "Guidance:\n"
             "- 1: No change in stakeholder groups.\n"
             "- 3: Some additional stakeholders are involved, but core groups remain unchanged.\n"
             "- 5: A significant shift with entirely new stakeholder groups."
         ),
         "regulatory_regime_shift": (
             "Regulatory Regime Shift: Does the change invoke a different set of legal or regulatory requirements?\n"
             "Guidance:\n"
             "- 1: No change in regulatory environment.\n"
             "- 3: Moderate change requiring some adjustments in compliance.\n"
             "- 5: Major shift necessitating entirely new regulatory considerations."
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
         "nature_of_change": (
             "Nature of Change: How significant is the modification?\n"
             "Guidance:\n"
             "- 1-2: Minor optimization or parameter tuning with negligible impact on core logic.\n"
             "- 3: Moderate modifications, such as replacing a minor component while retaining overall architecture.\n"
             "- 4-5: Fundamental redesign that alters the internal logic or core algorithm."
         ),
         "impact_on_model_structure": (
             "Impact on Model Structure: Do the changes affect core components or peripheral modules?\n"
             "Guidance:\n"
             "- 1: Changes are limited to peripheral or non-critical modules.\n"
             "- 3: Some core elements are affected, but overall structure remains intact.\n"
             "- 5: Major alterations to core components that significantly change the model's functionality."
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
         "data_volume_adjustment": (
             "Data Volume Adjustment: Does the change involve a significant increase or decrease in training data volume?\n"
             "Guidance:\n"
             "- 1: No significant change in volume.\n"
             "- 3: Moderate change (e.g., 20-30% increase or decrease).\n"
             "- 5: Large-scale change (e.g., doubling or halving the data)."
         ),
         "data_diversity": (
             "Data Diversity and Representativeness: Is there a notable change in the diversity of the training data?\n"
             "Guidance:\n"
             "- 1: No change in diversity.\n"
             "- 3: Some change in representativeness, affecting certain groups or scenarios moderately.\n"
             "- 5: A significant shift in data diversity that could impact bias or generalizability."
         ),
         "data_quality": (
             "Data Quality and Integrity: Does the new data have different quality standards or introduce noise/bias?\n"
             "Guidance:\n"
             "- 1: Data quality remains consistent.\n"
             "- 3: Moderate differences in quality or slight introduction of noise.\n"
             "- 5: Significant quality issues or bias introduced that impact model reliability."
         ),
         "retraining_impact": (
             "Retraining Impact: Does retraining on the new data alter performance metrics or risk profiles?\n"
             "Guidance:\n"
             "- 1: No measurable impact on performance.\n"
             "- 3: Moderate impact with some change in key metrics.\n"
             "- 5: Significant performance changes or emergence of new risk profiles."
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
         "quantitative_performance": (
             "Quantitative Performance Metrics: Rate the change in key performance metrics (accuracy, error rates, robustness).\n"
             "Guidance:\n"
             "- 1: No change in performance metrics.\n"
             "- 3: Moderate change (e.g., 5-10% difference).\n"
             "- 5: Severe change (e.g., >10% drop or significant improvement) affecting reliability."
         ),
         "qualitative_risk": (
             "Qualitative Risk Assessment: Does the modification introduce new risks (security vulnerabilities, ethical concerns)?\n"
             "Guidance:\n"
             "- 1: No new risks identified.\n"
             "- 3: Some new risks, but manageable or moderate in scope.\n"
             "- 5: Major new risks that could have significant adverse effects."
         ),
         "adversarial_testing": (
             "Adversarial and Robustness Testing: How does the change affect robustness under adversarial conditions?\n"
             "Guidance:\n"
             "- 1: Robustness remains unchanged.\n"
             "- 3: Moderate reduction in robustness under adversarial testing.\n"
             "- 5: Significant degradation in adversarial robustness."
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
         "integration_context": (
             "Integration Context Variation: Does the modification require changes to the deployment context (e.g., new hardware, software integrations)?\n"
             "Guidance:\n"
             "- 1: No change in deployment context.\n"
             "- 3: Moderate adjustments needed (e.g., minor hardware or software tweaks).\n"
             "- 5: Major changes requiring significant modifications to deployment environments."
         ),
         "end_user_experience": (
             "End-User Experience Impact: Does the modification change how end users interact with the system (UI, workflows)?\n"
             "Guidance:\n"
             "- 1: No impact on end-user experience.\n"
             "- 3: Some modifications in UI or workflow, but not disruptive.\n"
             "- 5: Significant impact, requiring a complete overhaul of user interaction."
         ),
         "regulatory_compliance": (
             "Regulatory Compliance Considerations: Does the change affect compliance by introducing new legal or policy challenges?\n"
             "Guidance:\n"
             "- 1: No change in compliance requirements.\n"
             "- 3: Moderate impact requiring some regulatory review.\n"
             "- 5: Major regulatory implications necessitating new compliance frameworks."
         )
    }
    future_deployment_scores = {}
    for key, question in future_deployment_subcriteria.items():
         future_deployment_scores[key] = st.radio(question, options=[1, 2, 3, 4, 5], key=f"future_{key}")
    future_deployment_avg = sum(future_deployment_scores.values()) / len(future_deployment_scores)
    st.write("Future Deployment Average Score:", round(future_deployment_avg, 2))

    # Calculate overall weighted score using the defined weights
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

    # Save the MCDA scores for later audit
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

# Scoring-based classification
if score >= 10:
    classification = "GPAI"
elif score >= 6:
    # Borderline scenario: prompt user to finalize classification
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