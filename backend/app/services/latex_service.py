"""
LaTeX compilation and Jinja2 template rendering service.

Provides:
- compile_latex_to_pdf: Compiles .tex source → PDF bytes
- render_template:      Fills a Jinja2-LaTeX template with data
- latex_escape:         Escapes LaTeX special characters
"""

import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Tuple

from jinja2 import Environment, BaseLoader

from app.core.logging import get_logger

logger = get_logger("latex_service")

# ── LaTeX special character escaping ─────────────────────────────────────

_LATEX_ESCAPE_MAP = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def latex_escape(value: str) -> str:
    """
    Escape LaTeX special characters in a string.

    Handles:
    - Standard LaTeX reserved characters: & % $ # _ { } ~ ^
    - Backslashes (must be first to avoid double-escaping)
    - Smart/unicode quotes and dashes → ASCII equivalents
    - Other problematic unicode characters
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)

    # ── 1. Normalize unicode before escaping ──────────────────────────
    # Smart quotes → plain ASCII
    value = value.replace("\u2018", "'").replace("\u2019", "'")  # ' '
    value = value.replace("\u201c", "''").replace("\u201d", "''")  # " "  → LaTeX-style double quotes
    # Dashes
    value = value.replace("\u2013", "--")   # en-dash → LaTeX --
    value = value.replace("\u2014", "---")  # em-dash → LaTeX ---
    # Ellipsis
    value = value.replace("\u2026", r"\ldots{}")
    # Bullet
    value = value.replace("\u2022", r"\textbullet{}")
    # Non-breaking space
    value = value.replace("\u00a0", "~")

    # ── 2. Strip any LaTeX commands that shouldn't be in data ─────────
    # Remove \textbf{...} → keep inner text
    value = re.sub(r'\\(?:textbf|textit|emph|underline|textsc)\{([^}]*)\}', r'\1', value)
    # Remove \href{url}{text} → keep text
    value = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', value)

    # ── 3. Escape backslash (must be before the map) ──────────────────
    value = value.replace("\\", r"\textbackslash{}")

    # ── 4. Escape the standard special characters ─────────────────────
    for char, replacement in _LATEX_ESCAPE_MAP.items():
        value = value.replace(char, replacement)

    return value


# ── Jinja2 environment with LaTeX-safe delimiters ───────────────────────

def _create_jinja_env() -> Environment:
    """
    Create a Jinja2 environment that uses << >> delimiters
    to avoid conflict with LaTeX's { } syntax.
    """
    env = Environment(
        loader=BaseLoader(),
        block_start_string="<<%",
        block_end_string="%>>",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="<<#",
        comment_end_string="#>>",
        autoescape=False,
    )
    env.filters["latex_escape"] = latex_escape
    return env


_jinja_env = _create_jinja_env()


def render_template(template_latex: str, data: dict) -> str:
    """
    Render a Jinja2-LaTeX template with the given data dictionary.

    Args:
        template_latex: LaTeX source with Jinja2 << >> placeholders.
        data: Dictionary of values to fill into the template.

    Returns:
        Rendered LaTeX source string.
    """
    template = _jinja_env.from_string(template_latex)
    rendered = template.render(data=data)

    # Post-render cleanup: fix common issues in the final LaTeX
    rendered = _sanitize_rendered_latex(rendered)

    return rendered


def _sanitize_rendered_latex(latex: str) -> str:
    """
    Post-render sanitization of the final LaTeX document.
    Fixes common problems that can cause compilation failures.
    """
    # Remove any stray unescaped special chars outside of LaTeX commands
    # This catches edge cases where data slips through without escaping

    # Fix doubled backslash-escapes that can happen with nested processing
    # e.g. \\\\& → \\&
    latex = re.sub(r'\\{3,}([&%$#_{}])', r'\\\1', latex)

    # Remove empty itemize environments (can happen with empty bullet lists)
    latex = re.sub(
        r'\\begin\{itemize\}[^\n]*\n\s*\\end\{itemize\}',
        '',
        latex,
        flags=re.MULTILINE,
    )

    # Remove consecutive blank lines (more than 2) to prevent LaTeX warnings
    latex = re.sub(r'\n{4,}', '\n\n\n', latex)

    return latex


def get_dummy_resume_data() -> dict:
    """Return dummy resume data for previewing templates."""
    return {
        "personal_info": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "+1 (555) 123-4567",
            "location": "San Francisco, CA",
            "linkedin": "https://linkedin.com/in/janedoe",
            "github": "https://github.com/janedoe",
        },
        "summary": "Experienced software engineer with a passion for building scalable infrastructure and delightful user experiences.",
        "work_experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullets": [
                    "Led the migration of legacy monolith to microservices.",
                    "Improved system performance by 40%.",
                ],
            },
            {
                "title": "Software Engineer",
                "company": "Startup Inc",
                "location": "New York, NY",
                "start_date": "Jun 2017",
                "end_date": "Dec 2019",
                "bullets": [
                    "Developed core features for the main web application.",
                    "Implemented CI/CD pipelines.",
                ],
            }
        ],
        "education": [
            {
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "institution": "University of Technology",
                "start_date": "2013",
                "end_date": "2017",
                "gpa": "3.8",
                "details": "Graduated with Honors",
            }
        ],
        "skills": {
            "technical": ["Python", "TypeScript", "Go"],
            "tools": ["Docker", "Kubernetes", "AWS"],
            "languages": ["English", "Spanish"],
        },
        "projects": [
            {
                "name": "Open Source Project",
                "description": "A popular open source library for data processing.",
                "url": "https://github.com/janedoe/project",
                "technologies": ["Python", "Pandas"],
                "bullets": ["Over 1,000 GitHub stars on the repository."],
            }
        ],
        "certifications": [
            "AWS Certified Solutions Architect",
        ],
        "achievements": [
            "Employee of the Year 2021",
        ],
    }


# ── LaTeX → PDF compilation ─────────────────────────────────────────────

def _find_latex_compiler() -> str:
    """Detect available LaTeX compiler on the system."""
    for compiler in ("pdflatex", "tectonic", "xelatex", "lualatex"):
        if shutil.which(compiler):
            logger.info("Found LaTeX compiler: %s", compiler)
            return compiler
    raise RuntimeError(
        "No LaTeX compiler found. Install pdflatex (TeX Live / MiKTeX) "
        "or tectonic and ensure it's on the system PATH."
    )


def validate_latex(latex_code: str) -> list[str]:
    """
    Pre-compilation validation to catch common LaTeX issues.
    Returns a list of warnings/issues found.
    """
    issues = []

    # Check for balanced begin/end environments
    begins = re.findall(r'\\begin\{(\w+)\}', latex_code)
    ends = re.findall(r'\\end\{(\w+)\}', latex_code)

    begin_counts = {}
    for env in begins:
        begin_counts[env] = begin_counts.get(env, 0) + 1
    end_counts = {}
    for env in ends:
        end_counts[env] = end_counts.get(env, 0) + 1

    for env in set(list(begin_counts.keys()) + list(end_counts.keys())):
        b = begin_counts.get(env, 0)
        e = end_counts.get(env, 0)
        if b != e:
            issues.append(f"Unbalanced environment '{env}': {b} begin vs {e} end")

    # Check for unescaped special characters outside of commands
    # Simple heuristic: look for bare & not preceded by \ and not inside \begin{} etc.
    lines = latex_code.splitlines()
    for i, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('%'):
            continue
        # Check for bare & (common issue with AI-generated text)
        bare_ampersands = re.findall(r'(?<!\\)&', line)
        # Filter out those inside tabular or align environments (where & is valid)
        if bare_ampersands and not any(env in line for env in ['tabular', 'align', 'array']):
            # This is actually valid in some contexts, just a warning
            pass

    # Check that document has basic structure
    if r'\documentclass' not in latex_code:
        issues.append("Missing \\documentclass declaration")
    if r'\begin{document}' not in latex_code:
        issues.append("Missing \\begin{document}")
    if r'\end{document}' not in latex_code:
        issues.append("Missing \\end{document}")

    return issues


def compile_latex_to_pdf(latex_code: str) -> Tuple[bytes, list[str]]:
    """
    Compile LaTeX source code into a PDF.

    Args:
        latex_code: Complete .tex source code.

    Returns:
        Tuple of (pdf_bytes, warnings).
        Raises RuntimeError on compilation failure.
    """
    # Pre-validate
    validation_issues = validate_latex(latex_code)
    if validation_issues:
        # Log warnings but only fail on critical issues
        critical = [i for i in validation_issues if 'Missing' in i]
        if critical:
            raise RuntimeError(
                "LaTeX validation failed:\n" + "\n".join(critical)
            )
        for issue in validation_issues:
            logger.warning("LaTeX validation: %s", issue)

    compiler = _find_latex_compiler()

    with tempfile.TemporaryDirectory(prefix="resumecraft_") as tmpdir:
        tex_path = Path(tmpdir) / "resume.tex"
        pdf_path = Path(tmpdir) / "resume.pdf"

        tex_path.write_text(latex_code, encoding="utf-8")
        logger.info("Compiling LaTeX with %s in %s", compiler, tmpdir)

        if compiler == "tectonic":
            cmd = [compiler, str(tex_path), "--outdir", tmpdir]
        else:
            # pdflatex / xelatex / lualatex
            cmd = [
                compiler,
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={tmpdir}",
                str(tex_path),
            ]

        # Run twice for cross-references (standard LaTeX practice)
        for run in range(2):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=tmpdir,
            )

            if result.returncode != 0 and (run == 1 or compiler == "tectonic"):
                # Only fail on the second pass for pdflatex, or first for tectonic
                error_lines = _extract_errors(result.stdout + "\n" + result.stderr)

                # Log the failing LaTeX for debugging
                import time
                ts = int(time.time())
                debug_tex = Path(tempfile.gettempdir()) / f"failed_resume_{ts}.tex"
                debug_tex.write_text(latex_code, encoding="utf-8")

                logger.error("LaTeX compilation failed. Source saved to %s", debug_tex)
                logger.error("Errors:\n%s", "\n".join(error_lines))

                raise RuntimeError(
                    f"LaTeX compilation failed:\n" + "\n".join(error_lines[:20])
                )

        if not pdf_path.exists():
            raise RuntimeError("PDF file was not produced by the LaTeX compiler.")

        warnings = _extract_warnings(result.stdout)
        pdf_bytes = pdf_path.read_bytes()
        logger.info("PDF compiled successfully (%d bytes)", len(pdf_bytes))
        return pdf_bytes, warnings


def _extract_errors(log_output: str) -> list[str]:
    """Extract error lines from LaTeX log output with context."""
    errors = []
    lines = log_output.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("!"):
            # Capture the error message
            errors.append(stripped)
            # Look for leading context (usually line number l.[number])
            for j in range(max(0, i-3), i):
                if lines[j].strip():
                    errors.insert(-1, lines[j].strip())
            # Capture the following context (where LaTeX shows the issue)
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip():
                    errors.append(lines[j].strip())
            break  # Typically the first fatal error is most relevant

    return errors if errors else ["Unknown error. Check LaTeX syntax."]


def _extract_warnings(log_output: str) -> list[str]:
    """Extract warning lines from LaTeX log output."""
    warnings = []
    for line in log_output.splitlines():
        if "Warning" in line or "Overfull" in line or "Underfull" in line:
            warnings.append(line.strip())
    return warnings
