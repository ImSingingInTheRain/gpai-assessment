import streamlit as st
import pandas as pd
import io

st.title("General-Purpose AI Model Classification Tool")

st.info("""
**Important:**  
If your organization uses a third-party model **without any modification**, you are **not considered a provider** under the AI Act and no further assessment is needed.
""")

# ----------------------
# Step 1: Automatic Exclusion
# ----------------------
st.header("Step 1: Automatic Exclusion Check")
st.markdown("""
**Criterion:** The AI model is exclusively specialized or narrowly focused without substantial capability to generalize or adapt flexibly across multiple distinct tasks.

**Examples:**
- Rule-based systems
- Small supervised classifiers (e.g., spam detection)
- Single-purpose NLP or vision models
- Specialized anomaly detection systems
- Traditional statistical models
- RPA systems
""")
auto_exclude = st.radio(
    "Does this exclusion criterion clearly apply to your AI model?",
    ['Yes', 'No'],
    key="auto_exclude"
)

if auto_exclude == 'Yes':
    st.error("Automatically discarded – Not GPAI.")
    st.stop()

# ----------------------
# Step 2: Provider Determination
# ----------------------
st.subheader("Step 2: Provider Determination")
developed_internally = st.radio(
    "Was the model developed internally or by a third party?",
    ["Internally Developed", "Third Party"],
    key="provider_determination"
)

if developed_internally == "Third Party":
    st.info("Since the model is from a third party, please assess modifications to determine if you're a provider.")
    
    st.subheader("Step 2a: Substantial Modification Assessment")
    
    mod_questions = {
        "param_change": ("Are more than 10% of parameters or architecture significantly changed?",
                         "Over 10% change typically indicates substantial modification."),
        "purpose_change": ("Has the intended purpose or functionality significantly changed or expanded?",
                           "Major task adaptations or new capabilities indicate substantial modification."),
        "data_change": ("Has significant retraining occurred on specialized or distinctly different datasets?",
                        "Extensive retraining with new datasets indicates substantial modification."),
        "integration_change": ("Does modification significantly alter downstream applicability or integration possibilities?",
                               "Major changes affecting downstream integration imply substantial modifications.")
    }
    
    mod_answers = {}
    for key, (question, guidance) in mod_questions.items():
        mod_answers[key] = st.radio(question, ["Yes", "No"], key=f"mod_{key}")
        st.markdown(f"<small>{guidance}</small>", unsafe_allow_html=True)
    
    if "Yes" in mod_answers.values():
        st.warning("Substantial modification – You are considered a provider under the AI Act. Proceed to pre-screening.")
    else:
        st.success("Minor modification – Not considered a provider. No further obligations apply.")
        st.stop()

# ----------------------
# Step 3: Pre-screening Questions
# ----------------------
st.subheader("Step 3: Pre-screening Questions")

pre_questions = {
    "params_below": ("Is the model's parameter count significantly below 1 billion?",
                     "Models significantly below 1 billion parameters lack significant generality."),
    "trained_specialized": ("Was the model trained on highly specialized or limited data rather than large and diverse datasets?",
                            "General-purpose models typically require large and diverse datasets."),
    "single_task": ("Does the model exclusively demonstrate competent performance on a single or very narrow task?",
                    "General-purpose models must perform multiple distinct tasks."),
    "adaptability": ("Is there no clear pathway to adapt the model to different downstream tasks?",
                     "Adaptability via fine-tuning or APIs is required.")
}

pre_answers = {}
for key, (question, guidance) in pre_questions.items():
    pre_answers[key] = st.radio(question, ["Yes", "No"], key=f"pre_{key}")
    st.markdown(f"<small>{guidance}</small>", unsafe_allow_html=True)

if (
    (pre_answers["params_below"] == "Yes" and pre_answers["trained_specialized"] == "Yes")
    or pre_answers["single_task"] == "Yes"
    or pre_answers["adaptability"] == "Yes"
):
    st.error("Eliminated (Not GPAI)")
    st.stop()

# ----------------------
# Step 4: Detailed GPAI Assessment
# ----------------------
st.subheader("Step 4: Detailed GPAI Assessment")

score = 0
answers = {}

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

# Determine classification based on score
if score >= 10:
    classification = "GPAI"
elif score >= 6:
    # Borderline scenario: let user pick final classification
    classification = st.radio(
        "Borderline outcome – classify this model as:",
        ["GPAI", "Not GPAI"],
        key="borderline"
    )
    manual_rationale = st.text_area("Provide rationale for this decision:", key="manual_rationale")
else:
    classification = "Not GPAI"

st.write("Final Classification: ", classification)

# ----------------------
# Step 5: Systemic Risk Assessment (ONLY if GPAI)
# ----------------------
if classification == "GPAI":
    st.subheader("Step 5: Systemic Risk Assessment")

    sys_risk_questions = {
        "flops": "Does the model training involve ≥10^25 floating-point operations (FLOP)?",
        "state_of_art": "Is the model state-of-the-art or pushing state-of-the-art?",
        "scalability": "Does the model have significant reach or scalability?",
        "scaffolding": "Can the model significantly enable harmful applications through scaffolding?"
    }

    sys_risk_answers = {}
    for key, question in sys_risk_questions.items():
        sys_risk_answers[key] = st.radio(question, ["Yes", "No"], key=f"sysrisk_{key}")

    # Determine systemic classification
    if sys_risk_answers["flops"] == "Yes" or sys_risk_answers["state_of_art"] == "Yes":
        systemic_classification = "GPAI with systemic risk"
    elif sys_risk_answers["scalability"] == "Yes" or sys_risk_answers["scaffolding"] == "Yes":
        # Borderline scenario for systemic risk
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

    # -------------------------------------
    # Obligations Visualization (Only if GPAI)
    # -------------------------------------
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
        # If user chose "Not GPAI with systemic risk" in borderline scenario
        st.warning("No obligations apply because the final classification is 'Not GPAI with systemic risk'.")