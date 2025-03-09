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
# Step 3a: Substantial Modification Assessment
# ---------------------------------------------
if developed_internally == "Third Party" and thirdparty_modified == "Yes":
    st.header("Step 3a: Substantial Modification Assessment")
    st.info("""
    Answer "Yes" or "No" to each question. Weights:
    - Intended Purpose Change (30%)
    - Architectural/Algorithmic Changes (25%)
    - Data/Training Changes (20%)
    - Performance Impact (15%)
    - Future Deployment Change (10%)

    **Total score ≥ 50% indicates substantial modifications.**
    """)

    criteria = {
        "purpose_change": ("Has intended purpose or functionality significantly changed?", 30),
        "arch_change": ("Are architecture/algorithm significantly altered?", 25),
        "data_change": ("Have training data or dataset composition significantly changed?", 20),
        "performance_change": ("Has the model’s performance or risk profile significantly changed?", 15),
        "future_deployment": ("Could future deployment/integration significantly change the model's behavior?", 10)
    }

    total_score = 0
    for key, (question, weight) in criteria.items():
        sub_mod_assessment[key] = st.radio(question, ["Yes", "No"], key=f"submod_{key}")
        total_score += weight if sub_mod_assessment[key] == "Yes" else 0
        st.markdown(f"<small>Weight: {weight}%</small>", unsafe_allow_html=True)

    st.write("**Cumulative Modification Score:**", total_score, "%")

    if total_score < 50:
        st.success("Minor modifications only—no provider obligations apply.")
        st.stop()
    else:
        st.warning("Substantial modifications identified—continue to detailed assessment.")

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
        borderline_text = "Borderline systemic risk – Further review recommended"
        st.warning(borderline_text)
        final_decision = st.radio(
            "Final systemic risk decision:",
            ["GPAI with systemic risk", "Not GPAI with systemic risk"],
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
        "Systemic Risk Classification": systemic_classification,
    }

    # Merge Step 2 answers (only if third party, otherwise might be empty)
    for k, v in mod_answers.items():
        all_data[f"Step2_ModAssessment_{k}"] = v
    
    # Merge Step 3 answers
    for k, v in pre_answers.items():
        all_data[f"Step3_PreScreen_{k}"] = v

    # Merge Step 4 answers
    for k, v in answers.items():
        all_data[f"Step4_Detailed_{k}"] = v

    # Merge Step 5 answers
    for k, v in sys_risk_answers.items():
        all_data[f"Step5_SysRisk_{k}"] = v

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