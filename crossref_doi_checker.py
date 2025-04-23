import requests
import csv
import time
import streamlit as st
import pandas as pd
from io import StringIO
import concurrent.futures

# === STREAMLIT INTERFACE ===
st.set_page_config(page_title="Crossref DOI Resolver Checker", layout="centered")
st.title("DOI Resolver Checker for Crossref")

st.markdown("""
This app connects to the Crossref API to fetch all DOIs for a given Crossref prefix and checks whether each DOI resolves correctly. Handy for some metadata maintenance 🧹

### ℹ️ How to Use

1. Enter a Crossref **DOI prefix** (e.g., `10.12345`)  
2. Click **“Check DOI Resolution”**  
3. See a table of **DOIs**, **resolved URLs**, **status codes**, and whether they resolved  
4. Optionally **download a CSV report**

---

**Created by:**  
Søren Vidmar  
🔗 [ORCID](https://orcid.org/0000-0003-3055-6053)  
🏫 Aalborg University  
📧 [sv@aub.aau.dk](mailto:sv@aub.aau.dk)  
📦 [GitHub](https://github.com/svidmar)
""")

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = []

prefix = st.text_input("DOI Prefix (e.g., 10.12345)")
start_check = st.button("Check DOI Resolution")

RETRY_DELAY = 2.0
MAX_RETRIES = 3
PER_PAGE = 1000
MAX_WORKERS = 10  # Parallel requests

def fetch_crossref_dois(prefix):
    base_url = f"https://api.crossref.org/works?filter=prefix:{prefix}&rows={PER_PAGE}"
    offset = 0
    dois = []
    while True:
        url = f"{base_url}&offset={offset}"
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Failed to fetch DOIs: {response.status_code}")
            return []
        data = response.json()
        items = data["message"].get("items", [])
        if not items:
            break
        for item in items:
            doi = item.get("DOI")
            dois.append(doi)
        offset += PER_PAGE
        time.sleep(1)
    return dois

def check_doi_resolves(doi):
    doi_url = f"https://doi.org/{doi}"
    retries = 0
    while retries <= MAX_RETRIES:
        try:
            response = requests.get(doi_url, allow_redirects=True, timeout=10)
            status_code = response.status_code
            final_url = response.url
            resolves = "Yes" if status_code in [200, 301, 302] else "No"
            return doi, final_url, resolves, status_code
        except requests.RequestException:
            retries += 1
            time.sleep(RETRY_DELAY)
    return doi, "Timeout/Error", "No", "Timeout/Error"

def generate_csv(results):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["DOI", "Resolved URL", "Resolves", "HTTP Status Code"])
    writer.writerows(results)
    return output.getvalue()

if start_check and prefix:
    st.session_state.results = []  # Clear only when a new check starts

    with st.spinner("Fetching DOIs from Crossref..."):
        dois = fetch_crossref_dois(prefix)

    if dois:
        st.info("Checking where DOIs resolve to... (this may take a minute)")
        progress_text = st.empty()
        progress_bar = st.progress(0)
        table_placeholder = st.empty()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(check_doi_resolves, doi): doi for doi in dois}
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                doi, resolved_url, resolves, status_code = future.result()
                st.session_state.results.append((doi, resolved_url, resolves, status_code))

                # Live update table
                df = pd.DataFrame(st.session_state.results, columns=["DOI", "Resolved URL", "Resolves", "HTTP Status Code"])
                table_placeholder.dataframe(df)
                progress_bar.progress((i + 1) / len(futures))
                progress_text.text(f"Checked {i + 1} of {len(futures)}")

        st.success("Resolution check complete!")
    else:
        st.warning("No DOIs found for this prefix.")
elif st.session_state.results:
    st.dataframe(pd.DataFrame(st.session_state.results, columns=["DOI", "Resolved URL", "Resolves", "HTTP Status Code"]))

# CSV export
if st.session_state.results:
    csv_data = generate_csv(st.session_state.results)
    st.download_button("📥 Download CSV Report", csv_data, file_name="resolved_urls_crossref.csv", mime="text/csv")

    # Summary chart
    df_summary = pd.DataFrame(st.session_state.results, columns=["DOI", "Resolved URL", "Resolves", "HTTP Status Code"])
    summary = df_summary["Resolves"].value_counts().reset_index()
    summary.columns = ["Resolves", "Count"]
    st.bar_chart(summary.set_index("Resolves"))

    # Failed DOI viewer
    fails = df_summary[df_summary["Resolves"] == "No"]
    if not fails.empty:
        st.subheader("❌ DOIs That Failed to Resolve")
        st.dataframe(fails.reset_index(drop=True))