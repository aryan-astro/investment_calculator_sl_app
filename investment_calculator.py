import streamlit as st
import pandas  as pd
import math
from math import gcd

# FORMATTING
# Make wide page
st.set_page_config(page_title="Investment Calculator", layout="wide")

st.title("Investment Calculator")

# Make two columns for input and output
left, right = st.columns([1, 1.6], gap="large")


# INPUTS
with left:
    st.write("### Input Data")

    initial_amount = st.number_input("Initial Amount ($)", min_value=0.0, value=1000.0, step=100.0)
    duration = st.number_input("Duration (years)", min_value=1, value=10, step=1)
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=5.0, step=0.1)
    compound_freq = st.selectbox("Compounding Frequency", options=["Annually", "Semi-Annually", "Quarterly", "Monthly"])
    additional_contribution = st.number_input("Additional Contribution ($ per period)", min_value=0.0, value=100.0, step=50.0)
    contribution_freq = st.selectbox("Contribution Frequency", options=["Monthly", "Quarterly", "Semi-Annually", "Annually"])
    contribute_at = st.selectbox("Contribute at", options=["beginning", "end"])


# CALCULATIONS
freq_map = {"Annually": 1, "Semi-Annually": 2, "Quarterly": 4, "Monthly": 12}

K = freq_map[compound_freq]        # compounding periods/year
M = freq_map[contribution_freq]    # contribution periods/year
Y = duration                       # years
N = int(M * Y)                     # number of contributions
i_nom = interest_rate / 100.0      # nominal annual rate

# base timeline = LCM of K and M
base = (K * M) // gcd(K, M)                    # base periods/year
# effective rate per base period
i_base = (1 + i_nom / K) ** (K / base) - 1
# growth across one contribution interval (s base steps)
s = base // M
i_contrib = (1 + i_base) ** s - 1

# future value of initial principal
fv_initial = initial_amount * (1 + i_base) ** (base * Y)

# future value of contributions (ordinary vs due)
if contribute_at == "beginning":
    fv_contrib = additional_contribution * (((1 + i_contrib) ** N - 1) / i_contrib) * (1 + i_contrib)
else:
    fv_contrib = additional_contribution * (((1 + i_contrib) ** N - 1) / i_contrib)

final_amount = fv_initial + fv_contrib
total_contribution = initial_amount + additional_contribution * N

# OUTPUTS
with left:
    clicked = st.button("Calculate")

if clicked:
    with right:
        st.write("### Results")
        st.write(f"Final Amount: ${final_amount:,.2f}")
        st.write(f"Total Money Invested: ${total_contribution:,.2f}")
        st.write(f"Total Profit Made: ${final_amount - total_contribution:,.2f}")

        timeline = [n / base for n in range(0, int(base * Y) + 1)]
        values = []
        baseline_values = []

        N_total = int(M * Y)  # total number of scheduled contributions over the whole horizon

        for n in range(0, int(base * Y) + 1):
            t = n / base

            # Growth line (existing portfolio value)
            fv_initial_t = initial_amount * (1 + i_base) ** n
            n_contrib_t = math.floor(t * M)

            if contribute_at == "beginning":
                fv_contrib_t = additional_contribution * (((1 + i_contrib) ** n_contrib_t - 1) / i_contrib) * (1 + i_contrib)
            else:
                fv_contrib_t = additional_contribution * (((1 + i_contrib) ** n_contrib_t - 1) / i_contrib)

            values.append(fv_initial_t + fv_contrib_t)

            # Baseline (no growth only contributions)
            if contribute_at == "beginning":
                n_contrib_baseline = min(n_contrib_t + 1, N_total) if Y > 0 else 0
            else:
                n_contrib_baseline = min(n_contrib_t, N_total)

            baseline_values.append(initial_amount + additional_contribution * n_contrib_baseline)

        df = pd.DataFrame({
            "Time (years)": timeline,
            "Portfolio Value ($)": values,
            "Total Invested ($)": baseline_values,
        })
        st.line_chart(df.set_index("Time (years)"))
