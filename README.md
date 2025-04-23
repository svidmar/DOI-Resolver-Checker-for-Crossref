# Crossref DOI Resolver Checker

This Streamlit app allows you to fetch all DOIs registered under a given **Crossref prefix** and check whether each DOI resolves correctly. It’s a handy tool for DOI and metadata maintenance.

## 🔧 Features

- Fetch all DOIs for a Crossref prefix
- Follow redirects to the final resolved URL
- Display live progress with status codes and resolution outcome
- Download a CSV report with results
- View a summary bar chart (`Yes` vs `No` resolution)
- Highlight failed DOI resolutions in a separate table

## 🧪 How to Use

1. Install the dependencies:
    ```bash
    pip install streamlit pandas requests
    ```

2. Run the app:
    ```bash
    streamlit run crossref_resolved_url_checker.py
    ```

3. In the app:
    - Enter your **DOI prefix** (e.g., `10.12345`)
    - Click **Check DOI Resolution**
    - View results live as they resolve
    - Optionally download the CSV or view failed DOIs

## 📦 Output Columns

- **DOI** — The DOI identifier
- **Resolved URL** — The final URL after redirect
- **Resolves** — Yes/No if the redirect was successful
- **HTTP Status Code** — The HTTP response code (e.g. 200, 404)

## 🙋 Author

**Søren Vidmar**  
[ORCID](https://orcid.org/0000-0003-3055-6053)  
Aalborg University  
[GitHub Profile](https://github.com/svidmar)  
[sv@aub.aau.dk](mailto:sv@aub.aau.dk)