"""
╔══════════════════════════════════════════════════════╗
║   DS Internship Skill Tracker  —  PyQt5 Desktop App  ║
║   Skills: Python, SQL, ML, Stats, Viz, DL, NLP       ║
║   Features: Quiz, Resume Parser, Roadmap, Companies  ║
╚══════════════════════════════════════════════════════╝

Install dependencies:
    pip install PyQt5 matplotlib

Run:
    python ds_skill_tracker.py
"""

import sys, json, os, random
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSlider, QProgressBar,
    QFrame, QScrollArea, QGridLayout, QTextEdit, QMessageBox,
    QFileDialog, QRadioButton, QButtonGroup, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter, QBrush, QPen, QLinearGradient

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ═══════════════════════════════════════════════════════════
#  CONSTANTS
# ═══════════════════════════════════════════════════════════
DATA_FILE = os.path.join(os.path.expanduser("~"), ".ds_skill_tracker.json")

SKILLS = [
    {"id": "python",  "name": "Python",              "color": "#6C63FF"},
    {"id": "sql",     "name": "SQL & Databases",      "color": "#00D4AA"},
    {"id": "ml",      "name": "Machine Learning",     "color": "#F4A261"},
    {"id": "stats",   "name": "Statistics",           "color": "#A78BFA"},
    {"id": "viz",     "name": "Data Visualization",   "color": "#22D3EE"},
    {"id": "dl",      "name": "Deep Learning",        "color": "#E36262"},
    {"id": "feature", "name": "Feature Engineering",  "color": "#4ADE80"},
    {"id": "nlp",     "name": "NLP",                  "color": "#F59E0B"},
]

QUIZ_BANK = {
    "python": {
        "label": "Python", "color": "#6C63FF",
        "questions": [
            {"q": "What does df.dropna() do in pandas?",
             "opts": ["Fills NaN with 0", "Removes rows with NaN values", "Raises an error", "Returns NaN count"],
             "ans": 1},
            {"q": "Which method applies a function element-wise on a pandas Series?",
             "opts": [".apply()", ".map()", ".transform()", "All of the above"],
             "ans": 3},
            {"q": "What does zip(*matrix) do in Python?",
             "opts": ["Compresses the matrix", "Transposes a 2D list", "Creates a zip file", "Returns diagonal"],
             "ans": 1},
            {"q": "Which library is NOT typically used for Data Science?",
             "opts": ["Pandas", "NumPy", "Flask", "Scikit-learn"],
             "ans": 2},
            {"q": "What is the output type of np.array([1, 2, 3])?",
             "opts": ["list", "tuple", "numpy.ndarray", "array"],
             "ans": 2},
        ]
    },
    "ml": {
        "label": "Machine Learning", "color": "#F4A261",
        "questions": [
            {"q": "What does 'overfitting' mean in Machine Learning?",
             "opts": ["Model is too simple", "Model fits training data too well but fails on unseen data",
                      "Model never converges", "Model has high bias"],
             "ans": 1},
            {"q": "Which algorithm uses kernel tricks for non-linear classification?",
             "opts": ["Linear Regression", "K-Means", "SVM with RBF kernel", "Naive Bayes"],
             "ans": 2},
            {"q": "What does cross-validation primarily help with?",
             "opts": ["Speeding up training", "Estimating model generalization performance",
                      "Feature selection", "Data augmentation"],
             "ans": 1},
            {"q": "What is the purpose of regularization in ML?",
             "opts": ["Increase model complexity", "Prevent overfitting by penalizing large weights",
                      "Speed up optimization", "Normalize input features"],
             "ans": 1},
            {"q": "In Random Forest, what is 'bagging'?",
             "opts": ["Removing outliers", "Training trees on random subsets of data",
                      "Pruning decision trees", "Boosting weak learners"],
             "ans": 1},
        ]
    },
    "stats": {
        "label": "Statistics", "color": "#A78BFA",
        "questions": [
            {"q": "What does a p-value < 0.05 typically indicate?",
             "opts": ["Strong correlation", "Result is statistically significant",
                      "Null hypothesis is true", "Large effect size"],
             "ans": 1},
            {"q": "What does the Central Limit Theorem state?",
             "opts": ["All distributions are normal",
                      "Sample means approach normal distribution as sample size increases",
                      "Standard deviation always equals 1", "Mean always equals median"],
             "ans": 1},
            {"q": "Which measure of central tendency is most resistant to outliers?",
             "opts": ["Mean", "Variance", "Median", "Standard deviation"],
             "ans": 2},
            {"q": "What is a Type I error?",
             "opts": ["False negative", "Missing a true effect",
                      "False positive — rejecting a true null hypothesis", "Model overfitting"],
             "ans": 2},
            {"q": "What does Pearson correlation measure?",
             "opts": ["Causation between variables",
                      "Linear relationship strength between two variables",
                      "Non-linear relationship", "Probability of an event"],
             "ans": 1},
        ]
    },
    "sql": {
        "label": "SQL", "color": "#00D4AA",
        "questions": [
            {"q": "What does GROUP BY do in SQL?",
             "opts": ["Sorts result set", "Groups rows that have the same values into summary rows",
                      "Filters individual rows", "Joins two tables"],
             "ans": 1},
            {"q": "Which JOIN returns ALL rows from both tables, including unmatched rows?",
             "opts": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
             "ans": 3},
            {"q": "What does the HAVING clause do?",
             "opts": ["Filters rows before grouping", "Filters groups after GROUP BY",
                      "Sorts grouped results", "Joins groups together"],
             "ans": 1},
            {"q": "What is a subquery?",
             "opts": ["A query nested inside another query", "A shortcut for JOIN",
                      "A stored procedure", "An index type"],
             "ans": 0},
            {"q": "Which SQL function returns the number of rows?",
             "opts": ["SUM()", "MAX()", "COUNT()", "LEN()"],
             "ans": 2},
        ]
    },
}

COMPANIES = [
    {"name": "Google",     "role": "Data Science Intern",       "min_score": 80, "tags": ["Python", "ML", "Stats"]},
    {"name": "Microsoft",  "role": "ML Research Intern",        "min_score": 75, "tags": ["Python", "DL", "ML"]},
    {"name": "Amazon",     "role": "Business Intelligence Intern","min_score": 65,"tags": ["SQL", "Python", "Viz"]},
    {"name": "Adobe",      "role": "Data Science Intern",       "min_score": 65, "tags": ["Python", "ML", "Stats"]},
    {"name": "NVIDIA",     "role": "AI Research Intern",        "min_score": 80, "tags": ["DL", "Python", "ML"]},
    {"name": "Flipkart",   "role": "Data Analyst Intern",       "min_score": 55, "tags": ["SQL", "Python", "Stats"]},
    {"name": "Razorpay",   "role": "Data Science Intern",       "min_score": 55, "tags": ["Python", "SQL", "Stats"]},
    {"name": "Zomato",     "role": "ML Intern",                 "min_score": 55, "tags": ["Python", "ML", "SQL"]},
    {"name": "Swiggy",     "role": "Data Engineering Intern",   "min_score": 50, "tags": ["Python", "SQL"]},
    {"name": "Ola",        "role": "Analytics Intern",          "min_score": 45, "tags": ["SQL", "Viz", "Stats"]},
    {"name": "Paytm",      "role": "Data Analyst Intern",       "min_score": 40, "tags": ["SQL", "Viz"]},
    {"name": "Infosys",    "role": "AI/ML Intern",              "min_score": 35, "tags": ["Python", "ML"]},
]

ROADMAP = [
    {"title": "Python Foundations",       "skill": "python",  "threshold": 30,
     "desc": "NumPy, Pandas, core Python for data tasks.",
     "resources": ["Kaggle Python Course", "W3Schools Python", "NumPy Docs"]},
    {"title": "SQL & Data Querying",      "skill": "sql",     "threshold": 35,
     "desc": "Complex queries, JOINs, window functions.",
     "resources": ["SQLZoo", "LeetCode SQL", "Mode Analytics SQL"]},
    {"title": "Statistics Fundamentals",  "skill": "stats",   "threshold": 40,
     "desc": "Distributions, hypothesis testing, Bayesian basics.",
     "resources": ["StatQuest YouTube", "Khan Academy Stats", "Think Stats Book"]},
    {"title": "Data Visualization",       "skill": "viz",     "threshold": 45,
     "desc": "Matplotlib, Seaborn, Plotly — tell stories with data.",
     "resources": ["Matplotlib Docs", "Seaborn Gallery", "Plotly Tutorials"]},
    {"title": "Machine Learning Core",    "skill": "ml",      "threshold": 50,
     "desc": "Regression, classification, clustering, evaluation.",
     "resources": ["Scikit-learn Docs", "Andrew Ng Coursera", "Kaggle ML Course"]},
    {"title": "Feature Engineering",      "skill": "feature", "threshold": 55,
     "desc": "Transform raw data into powerful ML features.",
     "resources": ["Kaggle FE Tutorial", "Towards Data Science", "Feature Engineering Book"]},
    {"title": "Deep Learning Intro",      "skill": "dl",      "threshold": 65,
     "desc": "Neural networks, CNNs, RNNs — TensorFlow/PyTorch.",
     "resources": ["fast.ai DL", "PyTorch Tutorials", "Deep Learning Book"]},
    {"title": "NLP Basics",              "skill": "nlp",     "threshold": 70,
     "desc": "Text processing, transformers, sentiment analysis.",
     "resources": ["Hugging Face Course", "NLTK Book", "spaCy Docs"]},
]

# ═══════════════════════════════════════════════════════════
#  STYLES
# ═══════════════════════════════════════════════════════════
DARK_BG      = "#0D0F14"
SURFACE      = "#161920"
CARD_BG      = "#1C2030"
BORDER       = "#2A2D3A"
TEXT         = "#E8EAF0"
MUTED        = "#7A8199"
ACCENT       = "#6C63FF"
ACCENT2      = "#00D4AA"
WARN         = "#F4A261"
DANGER       = "#E36262"
SUCCESS      = "#4ADE80"

STYLE_SHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT};
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: {SURFACE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: #5A52E0;
}}
QPushButton:pressed {{
    background-color: #4A42D0;
}}
QPushButton#outline {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT};
}}
QPushButton#outline:hover {{
    background-color: rgba(255,255,255,0.05);
}}
QPushButton#success_btn {{
    background-color: rgba(74,222,128,0.15);
    border: 1px solid rgba(74,222,128,0.3);
    color: {SUCCESS};
}}
QPushButton#danger_btn {{
    background-color: rgba(227,98,98,0.12);
    border: 1px solid rgba(227,98,98,0.25);
    color: {DANGER};
}}
QSlider::groove:horizontal {{
    height: 6px;
    background: {BORDER};
    border-radius: 3px;
}}
QSlider::handle:horizontal {{
    background: {ACCENT};
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 3px;
}}
QProgressBar {{
    background-color: {BORDER};
    border-radius: 5px;
    height: 8px;
    text-align: center;
    border: none;
}}
QProgressBar::chunk {{
    border-radius: 5px;
}}
QTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT};
    padding: 8px;
    font-size: 13px;
}}
QTextEdit:focus {{
    border: 1px solid {ACCENT};
}}
QRadioButton {{
    color: {TEXT};
    font-size: 13px;
    padding: 8px;
    spacing: 10px;
}}
QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid {BORDER};
    background: transparent;
}}
QRadioButton::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}
QRadioButton:hover {{
    color: white;
}}
"""

# ═══════════════════════════════════════════════════════════
#  HELPER WIDGETS
# ═══════════════════════════════════════════════════════════
def make_card(parent=None):
    card = QFrame(parent)
    card.setStyleSheet(f"""
        QFrame {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
        }}
    """)
    return card

def make_label(text, size=13, color=TEXT, bold=False, parent=None):
    lbl = QLabel(text, parent)
    lbl.setStyleSheet(f"color:{color}; font-size:{size}px; {'font-weight:700;' if bold else ''} background:transparent; border:none;")
    lbl.setWordWrap(True)
    return lbl

def make_badge(text, color=ACCENT, bg=None):
    lbl = QLabel(text)
    bg = bg or f"rgba(108,99,255,0.15)"
    lbl.setStyleSheet(f"""
        color:{color};
        background:{bg};
        border-radius:99px;
        padding:2px 10px;
        font-size:11px;
        font-weight:700;
    """)
    lbl.setFixedHeight(22)
    return lbl

def divider():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet(f"color:{BORDER}; background:{BORDER}; border:none; max-height:1px;")
    return line

# ═══════════════════════════════════════════════════════════
#  DATA MANAGER
# ═══════════════════════════════════════════════════════════
class DataManager:
    def __init__(self):
        self.skills = {s["id"]: 0 for s in SKILLS}
        self.history = []
        self.quizzes_done = 0
        self.streak = 0
        self.last_date = None
        self.load()

    def load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE) as f:
                    d = json.load(f)
                self.skills = d.get("skills", self.skills)
                self.history = d.get("history", [])
                self.quizzes_done = d.get("quizzes_done", 0)
                self.streak = d.get("streak", 0)
                self.last_date = d.get("last_date", None)
            except Exception:
                pass

    def save(self):
        with open(DATA_FILE, "w") as f:
            json.dump({
                "skills": self.skills,
                "history": self.history,
                "quizzes_done": self.quizzes_done,
                "streak": self.streak,
                "last_date": self.last_date,
            }, f, indent=2)

    def overall(self):
        vals = list(self.skills.values())
        return round(sum(vals) / len(vals)) if vals else 0

    def update_streak(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_date != today:
            self.streak += 1
            self.last_date = today

    def record_snapshot(self):
        self.update_streak()
        self.history.append({
            "date": datetime.now().strftime("%d %b"),
            "overall": self.overall(),
            "skills": dict(self.skills),
        })
        self.save()

    def companies_matched(self):
        ov = self.overall()
        return sum(1 for c in COMPANIES if ov >= c["min_score"] * 0.8)


# ═══════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════
class SidebarBtn(QPushButton):
    def __init__(self, icon, label, parent=None):
        super().__init__(parent)
        self.setText(f"  {icon}  {label}")
        self.setCheckable(True)
        self.setFixedHeight(44)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {MUTED};
                border: none;
                border-left: 3px solid transparent;
                border-radius: 0;
                text-align: left;
                padding-left: 16px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: {TEXT};
                background: rgba(255,255,255,0.04);
            }}
            QPushButton:checked {{
                color: {ACCENT};
                background: rgba(108,99,255,0.09);
                border-left: 3px solid {ACCENT};
                font-weight: 600;
            }}
        """)


# ═══════════════════════════════════════════════════════════
#  SKILL BAR ROW
# ═══════════════════════════════════════════════════════════
class SkillBarRow(QWidget):
    def __init__(self, skill_name, value, color, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(12)

        name_lbl = make_label(skill_name, size=13, color=TEXT)
        name_lbl.setFixedWidth(170)
        lay.addWidget(name_lbl)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(value)
        bar.setTextVisible(False)
        bar.setFixedHeight(8)
        bar.setStyleSheet(f"""
            QProgressBar {{ background:{BORDER}; border-radius:4px; border:none; }}
            QProgressBar::chunk {{ background:{color}; border-radius:4px; }}
        """)
        lay.addWidget(bar)

        pct = make_label(f"{value}%", size=13, color=MUTED, bold=True)
        pct.setFixedWidth(40)
        pct.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        lay.addWidget(pct)


# ═══════════════════════════════════════════════════════════
#  CHART CANVAS
# ═══════════════════════════════════════════════════════════
class ProgressChart(FigureCanvas):
    def __init__(self, history, parent=None):
        self.fig = Figure(figsize=(7, 2.8), facecolor=CARD_BG)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background:transparent;")
        self.plot(history)

    def plot(self, history):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(CARD_BG)
        self.fig.patch.set_facecolor(CARD_BG)

        if not history:
            ax.text(0.5, 0.5, "No history yet — complete an assessment!",
                    color=MUTED, ha='center', va='center', transform=ax.transAxes, fontsize=12)
            ax.axis('off')
            self.draw()
            return

        labels = [h["date"] for h in history[-10:]]
        values = [h["overall"] for h in history[-10:]]

        ax.fill_between(range(len(values)), values, alpha=0.15, color=ACCENT)
        ax.plot(range(len(values)), values, color=ACCENT, linewidth=2.5, marker='o',
                markersize=6, markerfacecolor=ACCENT2, markeredgecolor='none')

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, color=MUTED, fontsize=10)
        ax.set_ylim(0, 105)
        ax.tick_params(axis='y', colors=MUTED, labelsize=10)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color(BORDER)
        ax.spines['left'].set_color(BORDER)
        ax.set_ylabel("Overall Score %", color=MUTED, fontsize=10)
        ax.grid(axis='y', color=BORDER, linestyle='--', alpha=0.5)
        self.fig.tight_layout(pad=1.0)
        self.draw()


class RadarChart(FigureCanvas):
    def __init__(self, skills_dict, parent=None):
        self.fig = Figure(figsize=(5, 4), facecolor=CARD_BG)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background:transparent;")
        self.plot(skills_dict)

    def plot(self, skills_dict):
        import numpy as np
        self.fig.clear()
        ax = self.fig.add_subplot(111, polar=True)
        ax.set_facecolor(CARD_BG)
        self.fig.patch.set_facecolor(CARD_BG)

        labels = [s["name"] for s in SKILLS]
        values = [skills_dict.get(s["id"], 0) for s in SKILLS]
        N = len(labels)
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        angles += angles[:1]
        values += values[:1]

        ax.set_theta_offset(3.14159 / 2)
        ax.set_theta_direction(-1)
        ax.set_rlabel_position(0)
        ax.set_ylim(0, 100)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(["25", "50", "75", "100"], color=MUTED, size=8)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, color=TEXT, size=9)
        ax.grid(color=BORDER, linestyle='--', alpha=0.5)
        ax.spines['polar'].set_color(BORDER)

        ax.fill(angles, values, color=ACCENT, alpha=0.2)
        ax.plot(angles, values, color=ACCENT2, linewidth=2)
        ax.plot(angles, values, 'o', color=ACCENT, markersize=5)

        self.fig.tight_layout(pad=0.5)
        self.draw()


# ═══════════════════════════════════════════════════════════
#  PAGES
# ═══════════════════════════════════════════════════════════

# ── Dashboard ──────────────────────────────────────────────
class DashboardPage(QWidget):
    navigate = pyqtSignal(int)

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(40, 36, 40, 40)

        # Title
        title = make_label("Your DS Journey", size=30, bold=True)
        title.setStyleSheet(f"color:{TEXT}; font-size:30px; font-weight:700; background:transparent; border:none;")
        root.addWidget(title)
        sub = make_label("Track, improve, and land your Data Science internship.", size=13, color=MUTED)
        sub.setContentsMargins(0, 4, 0, 24)
        root.addWidget(sub)

        # Stat cards row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)
        self.stat_overall = self._stat_card("—", "Overall Score")
        self.stat_quizzes = self._stat_card("0", "Quizzes Done")
        self.stat_companies = self._stat_card("0", "Companies Matched")
        self.stat_streak = self._stat_card("0", "Day Streak")
        for w in [self.stat_overall, self.stat_quizzes, self.stat_companies, self.stat_streak]:
            stats_row.addWidget(w)
        root.addLayout(stats_row)
        root.addSpacing(20)

        # Skill snapshot + radar
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # Skill bars card
        snap_card = make_card()
        snap_layout = QVBoxLayout(snap_card)
        snap_layout.setContentsMargins(24, 20, 24, 20)
        snap_layout.setSpacing(6)
        snap_layout.addWidget(make_label("Skill Snapshot", size=15, bold=True))
        snap_layout.addSpacing(8)
        self.bar_container = QVBoxLayout()
        self.bar_container.setSpacing(2)
        snap_layout.addLayout(self.bar_container)
        snap_layout.addSpacing(12)
        snap_layout.addWidget(divider())
        snap_layout.addSpacing(10)
        btn_row = QHBoxLayout()
        assess_btn = QPushButton("⊙  Start Assessment")
        assess_btn.clicked.connect(lambda: self.navigate.emit(1))
        quiz_btn = QPushButton("◻  Take Quiz")
        quiz_btn.setObjectName("outline")
        quiz_btn.clicked.connect(lambda: self.navigate.emit(2))
        btn_row.addWidget(assess_btn)
        btn_row.addWidget(quiz_btn)
        snap_layout.addLayout(btn_row)
        mid_row.addWidget(snap_card, 3)

        # Radar card
        radar_card = make_card()
        radar_layout = QVBoxLayout(radar_card)
        radar_layout.setContentsMargins(16, 20, 16, 20)
        radar_layout.addWidget(make_label("Skill Radar", size=15, bold=True))
        self.radar_placeholder = make_label("Complete assessment\nto see radar.", size=13, color=MUTED)
        self.radar_placeholder.setAlignment(Qt.AlignCenter)
        radar_layout.addWidget(self.radar_placeholder)
        self.radar_chart = None
        self.radar_layout = radar_layout
        mid_row.addWidget(radar_card, 2)

        root.addLayout(mid_row)
        root.addStretch()

    def _stat_card(self, val, label):
        card = make_card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        v = make_label(val, size=26, bold=True)
        v.setStyleSheet(f"color:{TEXT}; font-size:26px; font-weight:700; background:transparent; border:none;")
        l = make_label(label, size=12, color=MUTED)
        layout.addWidget(v)
        layout.addWidget(l)
        card._val = v
        return card

    def refresh(self):
        ov = self.dm.overall()
        self.stat_overall._val.setText(f"{ov}%")
        self.stat_quizzes._val.setText(str(self.dm.quizzes_done))
        self.stat_companies._val.setText(str(self.dm.companies_matched()))
        self.stat_streak._val.setText(str(self.dm.streak))

        # Refresh bars
        while self.bar_container.count():
            item = self.bar_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for s in SKILLS:
            row = SkillBarRow(s["name"], self.dm.skills.get(s["id"], 0), s["color"])
            self.bar_container.addWidget(row)

        # Refresh radar
        if self.radar_chart:
            self.radar_layout.removeWidget(self.radar_chart)
            self.radar_chart.deleteLater()
            self.radar_chart = None

        if any(v > 0 for v in self.dm.skills.values()):
            self.radar_placeholder.hide()
            self.radar_chart = RadarChart(self.dm.skills)
            self.radar_layout.addWidget(self.radar_chart)
        else:
            self.radar_placeholder.show()


# ── Assessment ─────────────────────────────────────────────
class AssessmentPage(QWidget):
    assessed = pyqtSignal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.sliders = {}
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 40)
        root.setSpacing(0)

        root.addWidget(make_label("Skill Assessment", size=28, bold=True))
        sub = make_label("Rate your proficiency from 0 (none) to 100 (expert).", size=13, color=MUTED)
        sub.setContentsMargins(0, 4, 0, 24)
        root.addWidget(sub)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none;}")

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        c_lay = QVBoxLayout(container)
        c_lay.setSpacing(16)
        c_lay.setContentsMargins(0, 0, 8, 0)

        for s in SKILLS:
            card = make_card()
            c_lay.addWidget(card)
            card_lay = QVBoxLayout(card)
            card_lay.setContentsMargins(22, 16, 22, 16)
            card_lay.setSpacing(8)

            header = QHBoxLayout()
            name_lbl = make_label(s["name"], size=14, bold=True)
            name_lbl.setStyleSheet(f"color:{s['color']}; font-size:14px; font-weight:700; background:transparent; border:none;")
            header.addWidget(name_lbl)
            header.addStretch()
            val_lbl = make_label(f"{self.dm.skills.get(s['id'], 0)}%", size=14, bold=True)
            val_lbl.setFixedWidth(44)
            val_lbl.setAlignment(Qt.AlignRight)
            header.addWidget(val_lbl)
            card_lay.addLayout(header)

            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(self.dm.skills.get(s["id"], 0))
            slider.setFixedHeight(28)

            lbl_ref = val_lbl
            slider.valueChanged.connect(lambda v, lbl=lbl_ref: lbl.setText(f"{v}%"))
            self.sliders[s["id"]] = slider
            card_lay.addWidget(slider)

        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        root.addSpacing(16)
        save_btn = QPushButton("💾  Save & Analyze Skills")
        save_btn.setFixedHeight(44)
        save_btn.clicked.connect(self.save_skills)
        root.addWidget(save_btn)

        # Resume section
        root.addSpacing(12)
        resume_card = make_card()
        r_lay = QVBoxLayout(resume_card)
        r_lay.setContentsMargins(22, 16, 22, 16)
        r_lay.addWidget(make_label("Or parse your resume text:", size=14, bold=True))
        self.resume_edit = QTextEdit()
        self.resume_edit.setPlaceholderText("Paste your resume text here and click Analyze…")
        self.resume_edit.setFixedHeight(100)
        r_lay.addWidget(self.resume_edit)
        parse_btn = QPushButton("🔍  Analyze Resume (AI)")
        parse_btn.setFixedHeight(38)
        parse_btn.clicked.connect(self.parse_resume)
        r_lay.addWidget(parse_btn)
        self.parse_result = make_label("", size=12, color=ACCENT2)
        r_lay.addWidget(self.parse_result)
        root.addWidget(resume_card)

    def save_skills(self):
        for sid, slider in self.sliders.items():
            self.dm.skills[sid] = slider.value()
        self.dm.record_snapshot()
        self.assessed.emit()
        QMessageBox.information(self, "Saved", "✓ Skills saved and analysis updated!")

    def parse_resume(self):
        text = self.resume_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Empty", "Please paste some resume text first.")
            return

        self.parse_result.setText("⏳ Analyzing with AI… (requires internet)")
        QApplication.processEvents()

        try:
            import urllib.request
            payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "messages": [{
                    "role": "user",
                    "content": (
                        "You are a Data Science internship coach. Analyze this resume and estimate "
                        "skill levels 0-100 for ONLY these keys: python, sql, ml, stats, viz, dl, feature, nlp.\n"
                        "Resume:\n" + text + "\n\n"
                        "Respond ONLY with a compact JSON object like: "
                        '{"python":70,"sql":50,"ml":40,"stats":60,"viz":30,"dl":10,"feature":35,"nlp":20}'
                    )
                }]
            }).encode()

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

            raw = data["content"][0]["text"].strip().replace("```json","").replace("```","")
            parsed = json.loads(raw)

            for k, v in parsed.items():
                if k in self.dm.skills:
                    self.dm.skills[k] = max(0, min(100, int(v)))
                    if k in self.sliders:
                        self.sliders[k].setValue(self.dm.skills[k])

            self.dm.record_snapshot()
            self.assessed.emit()
            self.parse_result.setText("✓ Resume analyzed! Skills updated.")
        except Exception as e:
            self.parse_result.setText(f"⚠ Could not reach AI API. Update sliders manually.\n({e})")


# ── Quiz ───────────────────────────────────────────────────
class QuizPage(QWidget):
    quiz_done = pyqtSignal()

    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.current_topic = None
        self.q_index = 0
        self.score = 0
        self.answered = False
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(40, 36, 40, 40)
        self.root.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")
        self.root.addWidget(self.stack)

        # Page 0: topic selection
        self.topic_page = QWidget()
        self.topic_page.setStyleSheet("background:transparent;")
        tp_lay = QVBoxLayout(self.topic_page)
        tp_lay.setContentsMargins(0,0,0,0)
        tp_lay.addWidget(make_label("Skill Quiz", size=28, bold=True))
        sub = make_label("Choose a topic to test your knowledge.", size=13, color=MUTED)
        sub.setContentsMargins(0,4,0,24)
        tp_lay.addWidget(sub)
        grid = QGridLayout()
        grid.setSpacing(14)
        topics = list(QUIZ_BANK.items())
        for i, (tid, tdata) in enumerate(topics):
            btn = QPushButton(f"{tdata['label']}\n{len(tdata['questions'])} questions  ·  Current: {self.dm.skills.get(tid,0)}%")
            btn.setFixedHeight(72)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background:{CARD_BG};
                    border:1px solid {BORDER};
                    border-radius:10px;
                    color:{TEXT};
                    font-size:13px;
                    text-align:center;
                }}
                QPushButton:hover {{
                    border-color:{tdata['color']};
                    background:rgba(108,99,255,0.07);
                }}
            """)
            btn.clicked.connect(lambda _, t=tid: self.start_quiz(t))
            grid.addWidget(btn, i // 2, i % 2)
        tp_lay.addLayout(grid)
        tp_lay.addStretch()
        self.stack.addWidget(self.topic_page)

        # Page 1: question
        self.q_page = QWidget()
        self.q_page.setStyleSheet("background:transparent;")
        qp_lay = QVBoxLayout(self.q_page)
        qp_lay.setContentsMargins(0,0,0,0)
        qp_lay.setSpacing(14)

        self.q_card = make_card()
        qc_lay = QVBoxLayout(self.q_card)
        qc_lay.setContentsMargins(28, 24, 28, 24)
        qc_lay.setSpacing(12)

        top_row = QHBoxLayout()
        self.q_progress = make_label("Q1/5", size=12, color=MUTED)
        top_row.addWidget(self.q_progress)
        top_row.addStretch()
        self.q_badge = make_badge("Python")
        top_row.addWidget(self.q_badge)
        qc_lay.addLayout(top_row)

        self.q_bar = QProgressBar()
        self.q_bar.setRange(0, 100)
        self.q_bar.setTextVisible(False)
        self.q_bar.setFixedHeight(4)
        self.q_bar.setStyleSheet(f"QProgressBar{{background:{BORDER};border-radius:2px;border:none;}} QProgressBar::chunk{{background:{ACCENT};border-radius:2px;}}")
        qc_lay.addWidget(self.q_bar)

        self.q_text = make_label("", size=15, bold=True)
        self.q_text.setStyleSheet(f"color:{TEXT}; font-size:15px; font-weight:600; background:transparent; border:none;")
        self.q_text.setWordWrap(True)
        qc_lay.addWidget(self.q_text)
        qc_lay.addSpacing(4)

        self.opt_buttons = []
        self.opt_group = QButtonGroup(self.q_page)
        self.opt_group.setExclusive(True)
        for i in range(4):
            rb = QRadioButton("")
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color:{MUTED};
                    font-size:13.5px;
                    padding:12px 14px;
                    background:{SURFACE};
                    border:1px solid {BORDER};
                    border-radius:8px;
                    spacing:12px;
                }}
                QRadioButton:hover {{
                    color:{TEXT};
                    border-color:{ACCENT};
                    background:rgba(108,99,255,0.07);
                }}
                QRadioButton::indicator {{ width:16px; height:16px; border-radius:8px; border:2px solid {BORDER}; }}
                QRadioButton::indicator:checked {{ background:{ACCENT}; border-color:{ACCENT}; }}
            """)
            self.opt_buttons.append(rb)
            self.opt_group.addButton(rb, i)
            qc_lay.addWidget(rb)

        qc_lay.addSpacing(6)
        qc_lay.addWidget(divider())
        qc_lay.addSpacing(6)

        nav_row = QHBoxLayout()
        exit_btn = QPushButton("← Exit Quiz")
        exit_btn.setObjectName("outline")
        exit_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        nav_row.addWidget(exit_btn)
        nav_row.addStretch()
        self.next_btn = QPushButton("Submit Answer →")
        self.next_btn.clicked.connect(self.submit_answer)
        nav_row.addWidget(self.next_btn)
        qc_lay.addLayout(nav_row)

        qp_lay.addWidget(self.q_card)
        self.stack.addWidget(self.q_page)

        # Page 2: results
        self.result_page = QWidget()
        self.result_page.setStyleSheet("background:transparent;")
        rp_lay = QVBoxLayout(self.result_page)
        rp_lay.setContentsMargins(0,0,0,0)
        rp_lay.setSpacing(16)
        rp_lay.addWidget(make_label("Quiz Complete! 🎉", size=26, bold=True))

        self.res_card = make_card()
        rc_lay = QVBoxLayout(self.res_card)
        rc_lay.setContentsMargins(28, 24, 28, 24)
        rc_lay.setSpacing(14)

        stat_r = QHBoxLayout()
        stat_r.setSpacing(12)
        self.res_score = self._stat_mini("—", "Score")
        self.res_correct = self._stat_mini("—", "Correct")
        self.res_level = self._stat_mini("—", "Level")
        stat_r.addWidget(self.res_score)
        stat_r.addWidget(self.res_correct)
        stat_r.addWidget(self.res_level)
        rc_lay.addLayout(stat_r)

        self.res_feedback = make_label("", size=13, color=TEXT)
        self.res_feedback.setWordWrap(True)
        self.res_feedback.setStyleSheet(f"background:rgba(108,99,255,0.08); color:{TEXT}; border:1px solid rgba(108,99,255,0.2); border-radius:8px; padding:14px; font-size:13px;")
        rc_lay.addWidget(self.res_feedback)

        rc_lay.addWidget(divider())
        rn_row = QHBoxLayout()
        retry = QPushButton("↺  Retake Quiz")
        retry.setObjectName("outline")
        retry.clicked.connect(lambda: self.start_quiz(self.current_topic))
        rn_row.addWidget(retry)
        rn_row.addStretch()
        topic_btn = QPushButton("Choose Topic")
        topic_btn.setObjectName("outline")
        topic_btn.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        rn_row.addWidget(topic_btn)
        rc_lay.addLayout(rn_row)
        rp_lay.addWidget(self.res_card)
        rp_lay.addStretch()
        self.stack.addWidget(self.result_page)

    def _stat_mini(self, val, label):
        f = QFrame()
        f.setStyleSheet(f"background:rgba(255,255,255,0.03); border:1px solid {BORDER}; border-radius:8px;")
        lay = QVBoxLayout(f)
        lay.setContentsMargins(12,10,12,10)
        v = make_label(val, size=22, bold=True)
        v.setStyleSheet(f"color:{TEXT}; font-size:22px; font-weight:700; background:transparent; border:none;")
        l = make_label(label, size=11, color=MUTED)
        lay.addWidget(v)
        lay.addWidget(l)
        f._val = v
        return f

    def start_quiz(self, topic_id):
        self.current_topic = topic_id
        self.q_index = 0
        self.score = 0
        self.answered = False
        self.stack.setCurrentIndex(1)
        self._load_question()

    def _load_question(self):
        topic = QUIZ_BANK[self.current_topic]
        qs = topic["questions"]
        q = qs[self.q_index]
        total = len(qs)

        self.q_progress.setText(f"Q{self.q_index+1} of {total}")
        self.q_bar.setValue(int((self.q_index / total) * 100))
        self.q_badge.setText(topic["label"])
        self.q_text.setText(q["q"])
        self.answered = False
        self.next_btn.setText("Submit Answer →")

        for rb in self.opt_buttons:
            rb.setChecked(False)
            rb.setStyleSheet(f"""
                QRadioButton {{
                    color:{MUTED}; font-size:13.5px; padding:12px 14px;
                    background:{SURFACE}; border:1px solid {BORDER}; border-radius:8px; spacing:12px;
                }}
                QRadioButton:hover {{ color:{TEXT}; border-color:{ACCENT}; background:rgba(108,99,255,0.07); }}
                QRadioButton::indicator {{ width:16px; height:16px; border-radius:8px; border:2px solid {BORDER}; }}
                QRadioButton::indicator:checked {{ background:{ACCENT}; border-color:{ACCENT}; }}
            """)

        for i, opt in enumerate(q["opts"]):
            self.opt_buttons[i].setText(opt)
            self.opt_buttons[i].setVisible(True)

    def submit_answer(self):
        if self.answered:
            self._next_or_finish()
            return

        selected = self.opt_group.checkedId()
        if selected == -1:
            QMessageBox.information(self, "Select an answer", "Please select an answer before submitting.")
            return

        self.answered = True
        topic = QUIZ_BANK[self.current_topic]
        correct = topic["questions"][self.q_index]["ans"]

        for i, rb in enumerate(self.opt_buttons):
            if i == correct:
                rb.setStyleSheet(f"""
                    QRadioButton {{ color:{SUCCESS}; font-size:13.5px; padding:12px 14px;
                    background:rgba(74,222,128,0.08); border:1px solid {SUCCESS}; border-radius:8px; spacing:12px; font-weight:600; }}
                    QRadioButton::indicator {{ width:16px; height:16px; border-radius:8px; border:2px solid {SUCCESS}; background:{SUCCESS}; }}
                """)
            elif i == selected:
                rb.setStyleSheet(f"""
                    QRadioButton {{ color:{DANGER}; font-size:13.5px; padding:12px 14px;
                    background:rgba(227,98,98,0.08); border:1px solid {DANGER}; border-radius:8px; spacing:12px; }}
                    QRadioButton::indicator {{ width:16px; height:16px; border-radius:8px; border:2px solid {DANGER}; background:{DANGER}; }}
                """)

        if selected == correct:
            self.score += 1

        self.next_btn.setText("Next Question →" if self.q_index < len(topic["questions"])-1 else "See Results →")

    def _next_or_finish(self):
        topic = QUIZ_BANK[self.current_topic]
        self.q_index += 1
        if self.q_index >= len(topic["questions"]):
            self._show_results()
        else:
            self.answered = False
            self._load_question()

    def _show_results(self):
        topic = QUIZ_BANK[self.current_topic]
        total = len(topic["questions"])
        pct = round((self.score / total) * 100)
        level = "Expert" if pct >= 80 else "Intermediate" if pct >= 60 else "Beginner" if pct >= 40 else "Novice"

        # Update skill
        old = self.dm.skills.get(self.current_topic, 0)
        self.dm.skills[self.current_topic] = max(old, pct)
        self.dm.quizzes_done += 1
        self.dm.record_snapshot()
        self.quiz_done.emit()

        self.res_score._val.setText(f"{pct}%")
        self.res_correct._val.setText(f"{self.score}/{total}")
        self.res_level._val.setText(level)

        msgs = {
            "Novice": "Keep going! Review the fundamentals and try again.",
            "Beginner": "Good start! Revisit concepts and practice more problems.",
            "Intermediate": "Solid knowledge! Tackle harder problems to reach Expert.",
            "Expert": "Outstanding! You're internship-ready in this topic. 🎉",
        }
        self.res_feedback.setText(
            f"You scored {pct}% on {topic['label']}. {msgs[level]}\n"
            f"Your skill level has been updated to {self.dm.skills[self.current_topic]}%."
        )
        self.stack.setCurrentIndex(2)

    def refresh(self):
        # refresh topic button labels
        pass


# ── Roadmap ────────────────────────────────────────────────
class RoadmapPage(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 40)
        root.setSpacing(0)

        root.addWidget(make_label("Learning Roadmap", size=28, bold=True))
        sub = make_label("Your personalized path to become internship-ready.", size=13, color=MUTED)
        sub.setContentsMargins(0, 4, 0, 24)
        root.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")

        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        self.c_lay = QVBoxLayout(self.content)
        self.c_lay.setContentsMargins(0, 0, 8, 0)
        self.c_lay.setSpacing(12)
        scroll.setWidget(self.content)
        root.addWidget(scroll, 1)

    def refresh(self):
        while self.c_lay.count():
            item = self.c_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, node in enumerate(ROADMAP):
            skill_val = self.dm.skills.get(node["skill"], 0)
            is_done = skill_val >= node["threshold"]
            prev_done = all(self.dm.skills.get(ROADMAP[j]["skill"], 0) >= ROADMAP[j]["threshold"] for j in range(i))
            is_next = not is_done and prev_done

            card = make_card()
            if is_done:
                card.setStyleSheet(f"QFrame{{background:rgba(0,212,170,0.07);border:1px solid rgba(0,212,170,0.25);border-radius:14px;}}")
            elif is_next:
                card.setStyleSheet(f"QFrame{{background:{CARD_BG};border:1px solid {ACCENT};border-radius:14px;}}")

            lay = QVBoxLayout(card)
            lay.setContentsMargins(24, 18, 24, 18)
            lay.setSpacing(8)

            # Header
            hrow = QHBoxLayout()
            dot_color = ACCENT2 if is_done else ACCENT if is_next else MUTED
            dot = make_label(f"{'✓' if is_done else str(i+1)}", size=12, bold=True, color=CARD_BG if is_done else dot_color)
            dot.setAlignment(Qt.AlignCenter)
            dot.setFixedSize(26, 26)
            dot.setStyleSheet(f"background:{dot_color if is_done else 'transparent'}; color:{CARD_BG if is_done else dot_color}; border-radius:13px; font-size:12px; font-weight:700; border:{'none' if is_done else f'2px solid {dot_color}'}; background:{'none' if not is_done else dot_color};")
            hrow.addWidget(dot)
            hrow.addSpacing(8)

            title_color = ACCENT2 if is_done else TEXT if is_next else MUTED
            title = make_label(node["title"], size=14, bold=True, color=title_color)
            title.setStyleSheet(f"color:{title_color}; font-size:14px; font-weight:700; background:transparent; border:none;")
            hrow.addWidget(title)
            hrow.addStretch()

            if is_done:
                hrow.addWidget(make_badge("✓ Complete", color=SUCCESS, bg="rgba(74,222,128,0.12)"))
            elif is_next:
                hrow.addWidget(make_badge("▶ Up Next", color=WARN, bg="rgba(244,162,97,0.12)"))
            else:
                hrow.addWidget(make_badge("🔒 Locked", color=MUTED, bg=f"rgba(122,129,153,0.1)"))
            lay.addLayout(hrow)

            desc = make_label(node["desc"], size=13, color=MUTED)
            lay.addWidget(desc)

            # Progress
            prog_row = QHBoxLayout()
            prog_row.addWidget(make_label(f"Required: {node['threshold']}%  ·  Current: {skill_val}%", size=12, color=MUTED))
            prog_row.addStretch()
            prog_bar = QProgressBar()
            prog_bar.setRange(0, node["threshold"])
            prog_bar.setValue(min(skill_val, node["threshold"]))
            prog_bar.setTextVisible(False)
            prog_bar.setFixedSize(120, 6)
            color = ACCENT2 if is_done else ACCENT if is_next else MUTED
            prog_bar.setStyleSheet(f"QProgressBar{{background:{BORDER};border-radius:3px;border:none;}} QProgressBar::chunk{{background:{color};border-radius:3px;}}")
            prog_row.addWidget(prog_bar)
            lay.addLayout(prog_row)

            # Resources
            res_row = QHBoxLayout()
            res_row.setSpacing(6)
            for r in node["resources"]:
                tag = QPushButton(r)
                tag.setFixedHeight(24)
                tag.setStyleSheet(f"""
                    QPushButton {{
                        background:rgba(108,99,255,0.1);
                        color:{ACCENT};
                        border:1px solid rgba(108,99,255,0.2);
                        border-radius:99px;
                        font-size:11px;
                        padding:0 10px;
                    }}
                    QPushButton:hover {{ background:rgba(108,99,255,0.2); }}
                """)
                res_row.addWidget(tag)
            res_row.addStretch()
            lay.addLayout(res_row)

            self.c_lay.addWidget(card)

        self.c_lay.addStretch()


# ── Companies ──────────────────────────────────────────────
class CompaniesPage(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 40)
        root.setSpacing(0)

        root.addWidget(make_label("Company Matches", size=28, bold=True))
        sub = make_label("Based on your current skill level — sorted by match.", size=13, color=MUTED)
        sub.setContentsMargins(0, 4, 0, 24)
        root.addWidget(sub)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent;border:none;")

        self.content = QWidget()
        self.content.setStyleSheet("background:transparent;")
        self.grid = QGridLayout(self.content)
        self.grid.setSpacing(14)
        self.grid.setContentsMargins(0, 0, 8, 0)
        scroll.setWidget(self.content)
        root.addWidget(scroll, 1)

    def refresh(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        ov = self.dm.overall()
        scored = sorted(
            [(c, min(100, max(0, round(ov - c["min_score"] + 60)))) for c in COMPANIES],
            key=lambda x: -x[1]
        )

        for idx, (company, match) in enumerate(scored):
            card = make_card()
            color = SUCCESS if match >= 70 else WARN if match >= 45 else DANGER
            card.setStyleSheet(f"QFrame{{background:{CARD_BG};border:1px solid {BORDER};border-radius:12px;}}")

            lay = QVBoxLayout(card)
            lay.setContentsMargins(18, 16, 18, 16)
            lay.setSpacing(6)

            top = QHBoxLayout()
            name = make_label(company["name"], size=14, bold=True)
            name.setStyleSheet(f"color:{TEXT};font-size:14px;font-weight:700;background:transparent;border:none;")
            top.addWidget(name)
            top.addStretch()
            badge_bg = f"rgba(74,222,128,0.13)" if match >= 70 else f"rgba(244,162,97,0.13)" if match >= 45 else f"rgba(227,98,98,0.1)"
            b = make_badge(f"{match}% match", color=color, bg=badge_bg)
            top.addWidget(b)
            lay.addLayout(top)

            lay.addWidget(make_label(company["role"], size=12, color=MUTED))

            # match bar
            mbar = QProgressBar()
            mbar.setRange(0, 100)
            mbar.setValue(match)
            mbar.setTextVisible(False)
            mbar.setFixedHeight(4)
            mbar.setStyleSheet(f"QProgressBar{{background:{BORDER};border-radius:2px;border:none;}} QProgressBar::chunk{{background:{color};border-radius:2px;}}")
            lay.addWidget(mbar)

            # tags
            tag_row = QHBoxLayout()
            tag_row.setSpacing(5)
            for t in company["tags"]:
                tl = make_label(t, size=11, color=MUTED)
                tl.setStyleSheet(f"color:{MUTED};background:{SURFACE};border:1px solid {BORDER};border-radius:99px;padding:1px 8px;font-size:11px;")
                tag_row.addWidget(tl)
            tag_row.addStretch()
            lay.addLayout(tag_row)

            # Required score hint
            req_txt = "✓ You qualify!" if ov >= company["min_score"] else f"Need {company['min_score']}% overall"
            lay.addWidget(make_label(req_txt, size=11, color=color))

            self.grid.addWidget(card, idx // 2, idx % 2)


# ── Progress ───────────────────────────────────────────────
class ProgressPage(QWidget):
    def __init__(self, dm: DataManager, parent=None):
        super().__init__(parent)
        self.dm = dm
        self.setStyleSheet("background:transparent;")
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 36, 40, 40)
        root.setSpacing(16)

        root.addWidget(make_label("Your Progress", size=28, bold=True))
        sub = make_label("Track your improvement over time.", size=13, color=MUTED)
        sub.setContentsMargins(0, 4, 0, 8)
        root.addWidget(sub)

        # Chart card
        chart_card = make_card()
        cc_lay = QVBoxLayout(chart_card)
        cc_lay.setContentsMargins(20, 20, 20, 20)
        cc_lay.addWidget(make_label("Overall Score History", size=15, bold=True))
        cc_lay.addSpacing(8)
        self.chart_container = QVBoxLayout()
        cc_lay.addLayout(self.chart_container)
        root.addWidget(chart_card)

        # All skills card
        skills_card = make_card()
        sc_lay = QVBoxLayout(skills_card)
        sc_lay.setContentsMargins(22, 20, 22, 20)
        sc_lay.addWidget(make_label("Current Skill Levels", size=15, bold=True))
        sc_lay.addSpacing(8)
        self.bars_container = QVBoxLayout()
        self.bars_container.setSpacing(6)
        sc_lay.addLayout(self.bars_container)
        root.addWidget(skills_card)

        root.addStretch()

        self._chart = None

    def refresh(self):
        # Chart
        if self._chart:
            self.chart_container.removeWidget(self._chart)
            self._chart.deleteLater()
        self._chart = ProgressChart(self.dm.history)
        self.chart_container.addWidget(self._chart)

        # Bars
        while self.bars_container.count():
            item = self.bars_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for s in SKILLS:
            self.bars_container.addWidget(
                SkillBarRow(s["name"], self.dm.skills.get(s["id"], 0), s["color"])
            )


# ═══════════════════════════════════════════════════════════
#  MAIN WINDOW
# ═══════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dm = DataManager()
        self.setWindowTitle("DS Internship Skill Tracker")
        self.setMinimumSize(1050, 700)
        self.resize(1180, 780)
        self.setStyleSheet(STYLE_SHEET)
        self._build_ui()
        self.go_to(0)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_lay = QHBoxLayout(central)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(f"QFrame{{background:{SURFACE};border-right:1px solid {BORDER};}}")
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(0, 0, 0, 0)
        sb_lay.setSpacing(0)

        logo = make_label("  SkillAI", size=20, bold=True)
        logo.setStyleSheet(f"color:{TEXT};font-size:20px;font-weight:700;background:transparent;border:none;padding:28px 22px 22px;")
        sb_lay.addWidget(logo)

        nav_items = [
            ("◈", "Dashboard"),
            ("⊙", "Assessment"),
            ("◻", "Quiz"),
            ("⟡", "Roadmap"),
            ("⊛", "Companies"),
            ("↗", "Progress"),
        ]
        self.nav_btns = []
        self.btn_group = QButtonGroup(sidebar)
        self.btn_group.setExclusive(True)
        for i, (icon, label) in enumerate(nav_items):
            btn = SidebarBtn(icon, label)
            self.btn_group.addButton(btn, i)
            btn.clicked.connect(lambda _, idx=i: self.go_to(idx))
            sb_lay.addWidget(btn)
            self.nav_btns.append(btn)

        sb_lay.addStretch()

        version = make_label("  v1.0 · DS Skill Tracker", size=11, color=MUTED)
        version.setContentsMargins(0, 0, 0, 12)
        sb_lay.addWidget(version)

        main_lay.addWidget(sidebar)

        # ── Pages ──
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        self.dash  = DashboardPage(self.dm)
        self.assess = AssessmentPage(self.dm)
        self.quiz  = QuizPage(self.dm)
        self.road  = RoadmapPage(self.dm)
        self.comp  = CompaniesPage(self.dm)
        self.prog  = ProgressPage(self.dm)

        for page in [self.dash, self.assess, self.quiz, self.road, self.comp, self.prog]:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("background:transparent;border:none;")
            scroll.setWidget(page)
            self.stack.addWidget(scroll)

        main_lay.addWidget(self.stack, 1)

        # Connect signals
        self.dash.navigate.connect(self.go_to)
        self.assess.assessed.connect(self.refresh_all)
        self.quiz.quiz_done.connect(self.refresh_all)

    def go_to(self, idx):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self.nav_btns):
            btn.setChecked(i == idx)
        self.refresh_page(idx)

    def refresh_page(self, idx):
        if idx == 0:  self.dash.refresh()
        if idx == 3:  self.road.refresh()
        if idx == 4:  self.comp.refresh()
        if idx == 5:  self.prog.refresh()

    def refresh_all(self):
        self.dash.refresh()
        self.road.refresh()
        self.comp.refresh()
        self.prog.refresh()


# ═══════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DS Internship Skill Tracker")

    # High-DPI support
    try:
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    except AttributeError:
        pass

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
