# University Career Insights Dashboard

A **Streamlit** and **Plotly** powered interactive dashboard for visualizing student career outcomes and engagement metrics at U.S. universities (2024–2025 cohort). This tool generates synthetic data, simulates realistic student behaviors, and presents key performance indicators (KPIs) through modern, dark-themed UI cards and charts.

---
## 🚀 Features

1. **Top KPI Cards** with sparklines:
   - Total Students
   - Full-Time Placement Rate (3-month rolling)
   - Median Days-to-Job (distribution)
   - Average Applications per Student

2. **Pipeline Conversion Funnel**:
   - Tracks Registered → Applicants → Shortlisted → Hired
   - Expandable info panel explaining each stage

3. **Major Overview Table**:
   - Students, Avg. Applications, Internship %, FT Placement %, Median Gap
   - Conditional color-scale on placement percentages

4. **University Ranking**:
   - Top 7 universities by FT placement rate
   - Shows student counts and placement %

5. **Internship Outcome Donut**:
   - % of students completing internships

6. **Event ROI Scatter Plot**:
   - Workshop Attendance vs. Interview Invites
   - Linear trendline quantifying ~25–30% lift

7. **Box-and-Whisker Plot**:
   - Distribution of days from graduation to full-time start by major

8. **Interactive Filters**:
   - Filter by Major and Graduation Year

---
## ⚙️ Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/Leneyxis/University-Metrics-Dashboard.git
   cd University-Metrics-Dashboard
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate    # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate synthetic data**
   ```bash
   python generate-data.py
   ```

5. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

---
## 📊 Data & Metrics

- **Synthetic Data Generation**: Uses Poisson & Gaussian distributions to simulate student registrations, logins, applications, event attendance, interview invites, internships, and placements.
- **Applicants**: Defined as students with ≥1 submitted application.
- **Event ROI**: Weighted sum of career fair, workshop, and info-session attendance, boosted for any resume workshop participation.
- **Placement Funnel**: Visualizes drop-off at each pipeline stage.
- **Internship & Placement Rates**: Shows conversion from internships to full-time roles.
- **Time-to-Employment**: Box plot highlights median and outliers in days-to-job.

---
## 🛠 Tech Stack

- **Streamlit** – Web app framework
- **Plotly** – Interactive data visualization
- **Pandas & NumPy** – Data manipulation & simulation
- **statsmodels** – Trendline regression for ROI chart

---
## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests for enhancements, bug fixes, or new metrics.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---
## 📄 License

This project is licensed under the [MIT License](LICENSE).
