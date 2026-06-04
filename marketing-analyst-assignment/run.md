# How to Run

## 1) Open the project folder

```powershell
cd "F:\project da\Marketing-Analytics-Assignments\marketing-analyst-assignment"
```

## 2) (Optional) Install dependencies

If you don’t already have them installed in your Python environment:

```powershell
python -m pip install -r .\requirements.txt
```

## 3) Build the unified dataset CSV

```powershell
python .\build_unified_ads.py --out .\unified_ads.csv
```

## 4) Run the dashboard

```powershell
$env:STREAMLIT_HOME = "$PWD\.streamlit"
streamlit run .\app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

Open:

- http://localhost:8501/

