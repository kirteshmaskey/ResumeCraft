"""
Seed script — inserts built-in LaTeX resume templates into the database.

Usage:
    cd backend
    python -m app.seed_templates
"""

import asyncio
from app.core.database import async_session_factory, engine, Base
import app.core.models  # noqa: F401 — register all models


SEED_TEMPLATES = [
    {
        "name": "Modern Professional",
        "description": "Clean, modern design with blue accent colors. Perfect for tech and business professionals.",
        "category": "professional",
        "latex_code": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.7in]{geometry}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{fontenc}

\definecolor{accent}{HTML}{2563EB}
\definecolor{darktext}{HTML}{1F2937}
\definecolor{lighttext}{HTML}{6B7280}

\hypersetup{colorlinks=true, urlcolor=accent}
\titleformat{\section}{\large\bfseries\color{accent}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{12pt}{6pt}
\pagestyle{empty}
\setlength{\parindent}{0pt}

\begin{document}

{\Huge\bfseries\color{darktext} << data.personal_info.name | latex_escape >>}\\\vspace{4pt}
{\color{lighttext}
<<% if data.personal_info.email %>>
\href{mailto:<< data.personal_info.email | latex_escape >>}{<< data.personal_info.email | latex_escape >>}
<<% endif %>>
<<% if data.personal_info.phone %>> $\mid$ << data.personal_info.phone | latex_escape >> <<% endif %>>
<<% if data.personal_info.location %>> $\mid$ << data.personal_info.location | latex_escape >> <<% endif %>>
<<% if data.personal_info.linkedin %>> $\mid$ \href{<< data.personal_info.linkedin >>}{LinkedIn} <<% endif %>>
<<% if data.personal_info.github %>> $\mid$ \href{<< data.personal_info.github >>}{GitHub} <<% endif %>>
}

<<% if data.summary %>>
\section{Professional Summary}
<< data.summary | latex_escape >>
<<% endif %>>

<<% if data.work_experience %>>
\section{Work Experience}
<<% for job in data.work_experience %>>
\textbf{<< job.title | latex_escape >>} \hfill << job.start_date | latex_escape >> -- << job.end_date | latex_escape >>\\
\textit{\color{lighttext}<< job.company | latex_escape >>}<<% if job.location %>> \hfill \textit{<< job.location | latex_escape >>}<<% endif %>>
<<% if job.bullets %>>
\begin{itemize}[nosep, leftmargin=1.5em]
  <<% for bullet in job.bullets %>>
  \item << bullet | latex_escape >>
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{4pt}
<<% endfor %>>
<<% endif %>>

<<% if data.education %>>
\section{Education}
<<% for edu in data.education %>>
\textbf{<< edu.degree | latex_escape >>}<<% if edu.field_of_study %>> in << edu.field_of_study | latex_escape >><<% endif %>> \hfill << edu.start_date | latex_escape >> -- << edu.end_date | latex_escape >>\\
\textit{\color{lighttext}<< edu.institution | latex_escape >>}<<% if edu.gpa %>> \hfill GPA: << edu.gpa | latex_escape >><<% endif %>>
\vspace{4pt}
<<% endfor %>>
<<% endif %>>

<<% if data.skills %>>
\section{Skills}
<<% if data.skills.technical %>>
\textbf{Technical:} << data.skills.technical | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.tools %>>
\textbf{Tools:} << data.skills.tools | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.languages %>>
\textbf{Languages:} << data.skills.languages | join(', ') | latex_escape >>
<<% endif %>>
<<% endif %>>

<<% if data.projects %>>
\section{Projects}
<<% for project in data.projects %>>
\textbf{<< project.name | latex_escape >>}<<% if project.technologies %>> \textit{\color{lighttext}(<< project.technologies | join(', ') | latex_escape >>)}<<% endif %>>\\
<< project.description | latex_escape >>
<<% if project.bullets %>>
\begin{itemize}[nosep, leftmargin=1.5em]
  <<% for bullet in project.bullets %>>
  \item << bullet | latex_escape >>
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{4pt}
<<% endfor %>>
<<% endif %>>

<<% if data.certifications %>>
\section{Certifications}
\begin{itemize}[nosep, leftmargin=1.5em]
<<% for cert in data.certifications %>>
  \item << cert | latex_escape >>
<<% endfor %>>
\end{itemize}
<<% endif %>>

\end{document}
""",
    },
    {
        "name": "Classic Academic",
        "description": "Traditional academic CV format with serif fonts. Ideal for research and academic applications.",
        "category": "academic",
        "latex_code": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=1in]{geometry}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}

\hypersetup{colorlinks=true, urlcolor=blue}
\titleformat{\section}{\large\bfseries\scshape}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{14pt}{8pt}
\pagestyle{empty}
\setlength{\parindent}{0pt}

\begin{document}

\begin{center}
{\LARGE\bfseries << data.personal_info.name | latex_escape >>}\\[6pt]
<<% if data.personal_info.email %>>
\href{mailto:<< data.personal_info.email | latex_escape >>}{<< data.personal_info.email | latex_escape >>}
<<% endif %>>
<<% if data.personal_info.phone %>> $\cdot$ << data.personal_info.phone | latex_escape >> <<% endif %>>
<<% if data.personal_info.location %>> $\cdot$ << data.personal_info.location | latex_escape >> <<% endif %>>
\\
<<% if data.personal_info.linkedin %>>
\href{<< data.personal_info.linkedin >>}{LinkedIn}
<<% endif %>>
<<% if data.personal_info.github %>> $\cdot$ \href{<< data.personal_info.github >>}{GitHub} <<% endif %>>
\end{center}

<<% if data.summary %>>
\section{Summary}
<< data.summary | latex_escape >>
<<% endif %>>

<<% if data.education %>>
\section{Education}
<<% for edu in data.education %>>
\textbf{<< edu.institution | latex_escape >>} \hfill << edu.start_date | latex_escape >> -- << edu.end_date | latex_escape >>\\
\textit{<< edu.degree | latex_escape >><<% if edu.field_of_study %>>, << edu.field_of_study | latex_escape >><<% endif %>>}<<% if edu.gpa %>> \hfill GPA: << edu.gpa | latex_escape >><<% endif %>>
<<% if edu.details %>>\\<< edu.details | latex_escape >><<% endif %>>
\vspace{6pt}
<<% endfor %>>
<<% endif %>>

<<% if data.work_experience %>>
\section{Experience}
<<% for job in data.work_experience %>>
\textbf{<< job.title | latex_escape >>}, << job.company | latex_escape >> \hfill << job.start_date | latex_escape >> -- << job.end_date | latex_escape >>
<<% if job.location %>>\\<< job.location | latex_escape >><<% endif %>>
<<% if job.bullets %>>
\begin{itemize}[nosep]
  <<% for bullet in job.bullets %>>
  \item << bullet | latex_escape >>
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{6pt}
<<% endfor %>>
<<% endif %>>

<<% if data.skills %>>
\section{Skills}
<<% if data.skills.technical %>>
\textbf{Technical Skills:} << data.skills.technical | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.tools %>>
\textbf{Tools \& Frameworks:} << data.skills.tools | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.languages %>>
\textbf{Languages:} << data.skills.languages | join(', ') | latex_escape >>
<<% endif %>>
<<% endif %>>

<<% if data.projects %>>
\section{Projects}
<<% for project in data.projects %>>
\textbf{<< project.name | latex_escape >>}
<<% if project.technologies %>>(\textit{<< project.technologies | join(', ') | latex_escape >>})<<% endif %>>
\\<< project.description | latex_escape >>
<<% if project.bullets %>>
\begin{itemize}[nosep]
  <<% for bullet in project.bullets %>>
  \item << bullet | latex_escape >>
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{6pt}
<<% endfor %>>
<<% endif %>>

<<% if data.certifications %>>
\section{Certifications}
\begin{itemize}[nosep]
<<% for cert in data.certifications %>>
  \item << cert | latex_escape >>
<<% endfor %>>
\end{itemize}
<<% endif %>>

<<% if data.achievements %>>
\section{Achievements}
\begin{itemize}[nosep]
<<% for ach in data.achievements %>>
  \item << ach | latex_escape >>
<<% endfor %>>
\end{itemize}
<<% endif %>>

\end{document}
""",
    },
    {
        "name": "Minimal Clean",
        "description": "Ultra-clean minimalist design with generous whitespace. For executives and senior professionals.",
        "category": "professional",
        "latex_code": r"""\documentclass[11pt,a4paper]{article}
\usepackage[margin=0.8in]{geometry}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{xcolor}

\definecolor{divider}{HTML}{E5E7EB}
\definecolor{muted}{HTML}{9CA3AF}

\hypersetup{colorlinks=true, urlcolor=black}
\pagestyle{empty}
\setlength{\parindent}{0pt}

\newcommand{\sectionrule}{\vspace{8pt}{\color{divider}\hrule height 0.5pt}\vspace{8pt}}

\begin{document}

{\LARGE\bfseries << data.personal_info.name | latex_escape >>}
\vspace{6pt}

{\small\color{muted}
<<% if data.personal_info.email %>><< data.personal_info.email | latex_escape >><<% endif %>>
<<% if data.personal_info.phone %>> | << data.personal_info.phone | latex_escape >><<% endif %>>
<<% if data.personal_info.location %>> | << data.personal_info.location | latex_escape >><<% endif %>>
<<% if data.personal_info.linkedin %>> | \href{<< data.personal_info.linkedin >>}{LinkedIn}<<% endif %>>
}

<<% if data.summary %>>
\sectionrule
<< data.summary | latex_escape >>
<<% endif %>>

<<% if data.work_experience %>>
\sectionrule
{\large\bfseries Experience}
\vspace{6pt}
<<% for job in data.work_experience %>>
\textbf{<< job.title | latex_escape >>} \hfill {\color{muted}<< job.start_date | latex_escape >> -- << job.end_date | latex_escape >>}\\
<< job.company | latex_escape >><<% if job.location %>> {\color{muted}| << job.location | latex_escape >>}<<% endif %>>
<<% if job.bullets %>>
\begin{itemize}[nosep, leftmargin=1.2em, label=\textbullet]
  <<% for bullet in job.bullets %>>
  \item << bullet | latex_escape >>
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{6pt}
<<% endfor %>>
<<% endif %>>

<<% if data.education %>>
\sectionrule
{\large\bfseries Education}
\vspace{6pt}
<<% for edu in data.education %>>
\textbf{<< edu.degree | latex_escape >>}<<% if edu.field_of_study %>>, << edu.field_of_study | latex_escape >><<% endif %>> \hfill {\color{muted}<< edu.start_date | latex_escape >> -- << edu.end_date | latex_escape >>}\\
<< edu.institution | latex_escape >>
\vspace{6pt}
<<% endfor %>>
<<% endif %>>

<<% if data.skills %>>
\sectionrule
{\large\bfseries Skills}
\vspace{4pt}
<<% if data.skills.technical %>>
<< data.skills.technical | join(' · ') | latex_escape >>
<<% endif %>>
<<% if data.skills.tools %>>
\\ << data.skills.tools | join(' · ') | latex_escape >>
<<% endif %>>
<<% endif %>>

\end{document}
""",
    },
    {
        "name": "Tech Engineer",
        "description": "Compact, dense layout optimized for software engineers. Emphasizes skills and projects.",
        "category": "tech",
        "latex_code": r"""\documentclass[10pt,a4paper]{article}
\usepackage[margin=0.6in]{geometry}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{xcolor}
\usepackage{multicol}

\definecolor{heading}{HTML}{111827}
\definecolor{link}{HTML}{2563EB}
\definecolor{subtle}{HTML}{6B7280}

\hypersetup{colorlinks=true, urlcolor=link}
\titleformat{\section}{\normalsize\bfseries\uppercase\color{heading}}{}{0em}{}[\titlerule]
\titlespacing*{\section}{0pt}{10pt}{4pt}
\pagestyle{empty}
\setlength{\parindent}{0pt}

\begin{document}

\begin{center}
{\Large\bfseries << data.personal_info.name | latex_escape >>}\\[4pt]
{\footnotesize\color{subtle}
<<% if data.personal_info.email %>>\href{mailto:<< data.personal_info.email | latex_escape >>}{<< data.personal_info.email | latex_escape >>}<<% endif %>>
<<% if data.personal_info.phone %>> $|$ << data.personal_info.phone | latex_escape >><<% endif %>>
<<% if data.personal_info.location %>> $|$ << data.personal_info.location | latex_escape >><<% endif %>>
<<% if data.personal_info.linkedin %>> $|$ \href{<< data.personal_info.linkedin >>}{LinkedIn}<<% endif %>>
<<% if data.personal_info.github %>> $|$ \href{<< data.personal_info.github >>}{GitHub}<<% endif %>>
}
\end{center}

<<% if data.summary %>>
\section{Summary}
{\small << data.summary | latex_escape >>}
<<% endif %>>

<<% if data.skills %>>
\section{Technical Skills}
{\small
<<% if data.skills.technical %>>
\textbf{Languages:} << data.skills.technical | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.tools %>>
\textbf{Tools \& Frameworks:} << data.skills.tools | join(', ') | latex_escape >>\\
<<% endif %>>
<<% if data.skills.languages %>>
\textbf{Spoken Languages:} << data.skills.languages | join(', ') | latex_escape >>
<<% endif %>>
}
<<% endif %>>

<<% if data.work_experience %>>
\section{Experience}
<<% for job in data.work_experience %>>
{\small\textbf{<< job.title | latex_escape >>} $|$ \textit{<< job.company | latex_escape >>} \hfill << job.start_date | latex_escape >> -- << job.end_date | latex_escape >>}
<<% if job.bullets %>>
\begin{itemize}[nosep, leftmargin=1.2em, itemsep=1pt]
  <<% for bullet in job.bullets %>>
  \item {\small << bullet | latex_escape >>}
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{2pt}
<<% endfor %>>
<<% endif %>>

<<% if data.projects %>>
\section{Projects}
<<% for project in data.projects %>>
{\small\textbf{<< project.name | latex_escape >>}<<% if project.technologies %>> [\textit{<< project.technologies | join(', ') | latex_escape >>}]<<% endif %>><<% if project.url %>> --- \href{<< project.url | latex_escape >>}{Link}<<% endif %>>}\\
{\small << project.description | latex_escape >>}
<<% if project.bullets %>>
\begin{itemize}[nosep, leftmargin=1.2em, itemsep=1pt]
  <<% for bullet in project.bullets %>>
  \item {\small << bullet | latex_escape >>}
  <<% endfor %>>
\end{itemize}
<<% endif %>>
\vspace{2pt}
<<% endfor %>>
<<% endif %>>

<<% if data.education %>>
\section{Education}
<<% for edu in data.education %>>
{\small\textbf{<< edu.degree | latex_escape >>}<<% if edu.field_of_study %>>, << edu.field_of_study | latex_escape >><<% endif %>> --- << edu.institution | latex_escape >> \hfill << edu.start_date | latex_escape >> -- << edu.end_date | latex_escape >>
<<% if edu.gpa %>> $|$ GPA: << edu.gpa | latex_escape >><<% endif %>>}
\vspace{2pt}
<<% endfor %>>
<<% endif %>>

\end{document}
""",
    },
]


async def seed():
    """Insert seed templates if they don't already exist."""
    from sqlalchemy import select
    from app.models.template import ResumeTemplate

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        for tmpl_data in SEED_TEMPLATES:
            existing_result = await session.execute(
                select(ResumeTemplate).where(ResumeTemplate.name == tmpl_data["name"])
            )
            template = existing_result.scalar_one_or_none()
            if template:
                print(f"  🔄  Updating template: {tmpl_data['name']}")
                for key, value in tmpl_data.items():
                    setattr(template, key, value)
            else:
                template = ResumeTemplate(**tmpl_data)
                session.add(template)
                print(f"  ✅ Created template: {tmpl_data['name']}")

        await session.commit()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
