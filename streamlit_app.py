import streamlit as st

st.title("General-Purpose AI Model (GPAI) Classification Tool")

st.info("""
**Important:**  
If you use a third-party model **without any modification**, you are **not considered a provider** under the AI Act and no further assessment is needed.
""")

st.subheader("Step 1: Automatic Exclusion Check")

st.markdown("""
If your model clearly fits into any of the following specialized categories, it can be automatically excluded:
- Rule-based Expert Systems
- Small-scale or Narrow ML Classifiers
- Traditional Statistical Models (e.g., linear regression)
- Single-purpose Computer Vision Models
- Single-purpose NLP Models
- Single-purpose Recommendation Systems
- Specialized Anomaly Detection Systems
- Robotic Process Automation (RPA) Systems
- Embedded Single-task IoT AI Systems
""")

auto_exclude = st.radio(
    "Does your model clearly belong to one of these specialized categories?",
    ['Yes', 'No']
)

if auto_exclude == 'Yes':
    st.error("Automatically excluded – Not a general-purpose AI model.")
    st.stop()

st.subheader("Step 2: Provider Determination")

developed_internally = st.radio(
    "Was the model developed internally or by a third party?",
    ['Internally Developed', 'Third Party']
)

if developed_internally == 'Third Party':
    st.info("You'll need to assess if your modifications are substantial later in the process.")

st.subheader("Step 3: Pre-screening Questions")

q1a = st.radio(
    "Is the model's parameter count significantly below 1 billion?",
    ['Yes', 'No']
)

q1b = st.radio(
    "Was the model trained on highly specialized or limited datasets (rather than large and diverse datasets)?",
    ['Yes', 'No']
)

q2 = st.radio(
    "Does the model exclusively demonstrate competent performance on a single or very narrow task?",
    ['Yes', 'No']
)

q3 = st.radio(
    "Is there no clear pathway (via fine-tuning, prompt engineering, or APIs) to adapt the model to different downstream tasks?",
    ['Yes', 'No']
)

if (q1a == 'Yes' and q1b == 'Yes') or q2 == 'Yes' or q3 == 'Yes':
    st.error("Eliminated (Not GPAI)")
else:
    st.success("Passed Pre-screening – Proceed to Detailed Assessment")

    if developed_internally == 'Third Party':
        st.subheader("Step 3a: Substantial Modification Assessment")

        mod1 = st.radio(
            "Have more than 10% of the model's parameters or architecture been significantly changed?",
            ['Yes', 'No']
        )
        mod2 = st.radio(
            "Has the intended purpose or functionality significantly changed or expanded?",
            ['Yes', 'No']
        )
        mod3 = st.radio(
            "Has significant retraining occurred on specialized or distinctly different datasets?",
            ['Yes', 'No']
        )
        mod4 = st.radio(
            "Does modification significantly alter the model’s ease of integration or use in diverse downstream systems?",
            ['Yes', 'No']
        )

        if 'Yes' in [mod1, mod2, mod3, mod4]:
            st.warning("Substantial Modification – You are considered a Provider under the AI Act.")
        else:
            st.success("Minor Modification – You are NOT considered a provider. No further obligations apply.")

    st.subheader("Step 4: Detailed GPAI Assessment")

    score = 0

    if st.radio(
        "Does the model have at least 1 billion parameters?",
        ['Yes', 'No']
    ) == 'Yes':
        score += 2

    training = st.radio(
        "Was the model trained on large and diverse datasets using self-supervision or other large-scale (semi-)unsupervised methods?",
        ['Yes', 'Partly', 'No']
    )
    score += {'Yes': 2, 'Partly': 1, 'No': 0}[training]

    tasks = st.radio(
        "Does the model demonstrate competent performance in multiple, distinct tasks?",
        ['Yes', 'Partly', 'No']
    )
    score += {'Yes': 2, 'Partly': 1, 'No': 0}[tasks]

    generative = st.radio(
        "Can the model generate new content (text, images, audio, or video) adaptable to various downstream tasks or domains?",
        ['Yes', 'Partly', 'No']
    )
    score += {'Yes': 2, 'Partly': 1, 'No': 0}[generative]

    modality = st.radio(
        "What data modality does the model handle?",
        ['Multi-modal', 'Single-flexible', 'Single-specialized']
    )
    score += {'Multi-modal': 2, 'Single-flexible': 1, 'Single-specialized': 0}[modality]

    adaptable = st.radio(
        "Can the model be readily integrated, fine-tuned, or prompt-engineered for new applications?",
        ['Yes', 'No']
    )
    score += 2 if adaptable == 'Yes' else 0

    use_cases = st.radio(
        "Are there multiple known or intended downstream use cases spanning different domains?",
        ['Yes', 'Partial', 'No']
    )
    score += {'Yes': 2, 'Partial': 1, 'No': 0}[use_cases]

    if score >= 10:
        st.success(f"Score: {score} – General-purpose AI model")
    elif score >= 6:
        st.warning(f"Score: {score} – Borderline: Further review recommended.")
    else:
        st.error(f"Score: {score} – Not a general-purpose AI model.")