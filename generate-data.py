import pandas as pd, numpy as np, random
from datetime import datetime, timedelta

# ── PARAMETERS ───────────────────────────────────────────────────
N_PER_MAJOR  = 500        # keeps 2 500 total
SEED         = 42
REG_START    = datetime(2024, 1, 1)
REG_END      = datetime(2025, 12, 31)

random.seed(SEED)
np.random.seed(SEED)

# ── LOOK-UPS ─────────────────────────────────────────────────────
majors = ["Computer Science", "Liberal Arts", "Business",
          "Engineering", "Life Sciences"]

intern_prob = {           # internship placement likelihood
    "Computer Science": .88, "Liberal Arts": .58,
    "Business": .72, "Engineering": .82, "Life Sciences": .68,
}

employers = [
    "Google","Microsoft","Amazon","Apple","Meta","Tesla",
    "Goldman Sachs","JPMorgan Chase","Deloitte","EY","Pfizer",
    "Johnson & Johnson","Intel","Cisco","General Electric"
]

industries = ["Tech","Finance","Healthcare","Education","Manufacturing"]

universities = [
    "Arizona State U.","UCLA","UT Austin","Ohio State",
    "Michigan","Georgia Tech","NYU","Florida","Penn State",
    "Purdue","UCSD","Boston University"
]

# ── HELPERS ─────────────────────────────────────────────────────
def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end-start).days))

def poisson_clip(lam, clip=0):                     # avoids 0 with small λ
    return max(clip, np.random.poisson(lam))

# ── GENERATE RECORDS ────────────────────────────────────────────
rows, sid = [], 1
for major in majors:
    for _ in range(N_PER_MAJOR):
        # ── IDs / static attributes
        sid_str  = f"S{sid:05d}"; sid += 1
        uni      = random.choice(universities)
        reg      = rand_date(REG_START, REG_END)
        grad     = reg + timedelta(days=random.randint(365*3,365*4))

        # ── Engagement factor (closer-to-grad students are busier)
        yrs_left = (grad - reg).days / 365
        eng_f    = 1.3 if yrs_left < 3.0 else 1.0

        # ── Usage
        logins             = poisson_clip(150 * eng_f)
        profile_completed   = np.random.binomial(1, 0.93)
        resume_uploads      = poisson_clip(3 * eng_f)

        # ── APPLICATIONS ( “Applicants” if >0 )
        apps_total = poisson_clip(35 * eng_f, clip=1)      # never 0

        # ── Events (major-aware means & sd)
        cf_mu  = 4 if major in ["Engineering","Computer Science"] else 2.5
        ws_mu  = 4 if major in ["Liberal Arts","Business"] else 3
        info_mu= 2

        career_fairs  = max(0, int(round(np.random.normal(cf_mu , 1.0))))
        workshops     = max(0, int(round(np.random.normal(ws_mu, 1.2))))
        info_sessions = max(0, int(round(np.random.normal(info_mu,0.8))))
        resume_ws     = int(workshops > 0)

        # ── INTERVIEW INVITES   (events → higher λ)
        # base λ grows with all event attendances; resume workshop amplifies
        lam_invites = (
            0.35 * career_fairs +
            0.55 * workshops +
            0.25 * info_sessions +
            1.5                               # floor
        ) * (1.25 if resume_ws else 1.0)       # 25 % boost

        invites     = min(apps_total, poisson_clip(lam_invites))
        shortlisted = np.random.binomial(invites, 0.52)

        # ── Internship
        intern_flag = np.random.binomial(1, intern_prob[major])
        if intern_flag:
            intern_start   = grad - timedelta(days=random.randint(90, 240))
            intern_emp     = random.choice(employers)
        else:
            intern_start   = pd.NaT
            intern_emp     = None

        # ── Full-time
        ft_flag = np.random.binomial(1, 0.82)
        if ft_flag:
            gap_days  = random.randint(30, 300)
            ft_start  = grad + timedelta(days=gap_days)
            ft_emp    = random.choice(employers)
        else:
            gap_days, ft_start, ft_emp = None, pd.NaT, None

        # ── Apps by industry
        apps_ind = {f"Applications_{ind}": poisson_clip(7) for ind in industries}

        # ── Row
        rows.append({
            "StudentID": sid_str, "University": uni, "Major": major,
            "RegisteredDate": reg, "GraduationDate": grad,
            "Logins": logins, "ProfileCompleted": profile_completed,
            "ResumeUploads": resume_uploads,
            "ApplicationsSubmitted": apps_total,         # → “Applicants”
            "CareerFairAttendance": career_fairs,
            "WorkshopAttendance": workshops,
            "InfoSessionAttendance": info_sessions,
            "ResumeWorkshopAttended": resume_ws,
            "InterviewInvites": invites,
            "ShortlistedCount": shortlisted,
            "InternshipPlacement": intern_flag,
            "InternshipEmployer": intern_emp,
            "InternshipStartDate": intern_start,
            "FullTimePlacement": ft_flag,
            "FullTimeEmployer": ft_emp,
            "FullTimePlacementDate": ft_start,
            "DaysToFullTimeJob": gap_days,
            **apps_ind
        })

# ── SAVE ────────────────────────────────────────────────────────
df = pd.DataFrame(rows)
df.to_csv("synthetic_career_dashboard_data.csv", index=False)
df.to_excel("synthetic_career_dashboard_data.xlsx", index=False)
