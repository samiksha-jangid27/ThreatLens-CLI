"""Build the editable report. Install .[docs]; render with LibreOffice for PDF/QA.

Example: python scripts/build_submission_report.py --benchmark benchmark.json
--validation validation.json --diagram architecture.png --output report.docx
"""

import argparse
import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


def build(benchmark, validation, diagram, output):
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    section.top_margin = section.bottom_margin = Inches(0.78)
    section.left_margin = section.right_margin = Inches(0.85)
    for name in ("Normal", "Title", "Subtitle", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = "Calibri"
        style.font.color.rgb = RGBColor(0, 0, 0)
    doc.styles["Caption"].font.color.rgb = RGBColor(0, 0, 0)
    # Word's default Title style can inherit an ornamental blue paragraph rule.
    for style in doc.styles:
        for border in list(style.element.iter(qn("w:pBdr"))):
            border.getparent().remove(border)
    normal = doc.styles["Normal"]
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.12
    doc.styles["Title"].font.size = Pt(27)
    doc.styles["Heading 1"].font.size = Pt(19)
    doc.styles["Heading 2"].font.size = Pt(12)
    for name in ("Heading 1", "Heading 2"):
        doc.styles[name].paragraph_format.keep_with_next = True
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run("ThreatLens 0.2  |  ")
    run.font.size = Pt(8)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    doc.core_properties.title = "ThreatLens behavioral compromise detection project report"
    doc.core_properties.author = "Samiksha Jangid"
    doc.core_properties.subject = "AI and ML application development class project"

    def p(text, style=None):
        return doc.add_paragraph(text, style)

    def heading(text):
        doc.add_heading(text, 2)

    def page(title):
        doc.add_page_break()
        doc.add_heading(title, 1)

    def code(text):
        paragraph = p(text)
        paragraph.paragraph_format.space_before = Pt(5)
        paragraph.paragraph_format.space_after = Pt(9)
        for run in paragraph.runs:
            run.font.name = "Courier New"
            fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
            for name in ("ascii", "hAnsi", "eastAsia", "cs"):
                fonts.set(qn("w:" + name), "Courier New")
            run.font.size = Pt(9)

    def table(headers, rows, widths=None):
        t = doc.add_table(rows=1, cols=len(headers))
        t.autofit = False
        if widths:
            for column, width in zip(t.columns, widths, strict=True):
                column.width = Inches(width)
        for cell, text in zip(t.rows[0].cells, headers, strict=True):
            cell.text = text
            shade = OxmlElement("w:shd")
            shade.set(qn("w:fill"), "EDEFF2")
            cell._tc.get_or_add_tcPr().append(shade)
            for run in cell.paragraphs[0].runs:
                run.bold = True
        for row in rows:
            cells = t.add_row().cells
            for cell, text in zip(cells, row, strict=True):
                cell.text = str(text)
        for row in t.rows:
            props = row._tr.get_or_add_trPr()
            props.append(OxmlElement("w:cantSplit"))
            for cell in row.cells:
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
                borders = OxmlElement("w:tcBorders")
                for edge in ("top", "left", "bottom", "right"):
                    item = OxmlElement("w:" + edge)
                    item.set(qn("w:val"), "single")
                    item.set(qn("w:sz"), "4")
                    item.set(qn("w:color"), "D9D9D9")
                    borders.append(item)
                cell._tc.get_or_add_tcPr().append(borders)
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.space_after = Pt(5)
                    paragraph.paragraph_format.space_before = Pt(5)
                    for run in paragraph.runs:
                        run.font.size = Pt(9.5)
        p("")
        return t

    p("ThreatLens behavioral compromise detection", "Title")
    p("Application development project report", "Subtitle")
    p("Samiksha Jangid\nVersion 0.2.0\n23 November 2026")
    heading("Abstract")
    p(
        "ThreatLens is a Python command-line tool that identifies behavioral deviations which may indicate device compromise without requiring known malicious hashes, addresses, domains or signatures. It learns trusted normal feature distributions and combines per-source Isolation Forest models with robust statistical deviation and repeated-window evidence. The result is an explainable investigation workflow for local hosts and exported infrastructure telemetry."
    )
    p(
        "The implementation supports system, router, firewall and network profiles through a validated observation contract, local psutil collectors and a native Zeek TSV importer. Frozen per-device baselines, explicit missing-source status, replay rejection, transactional state updates and persistent feature evidence improve the original project's reliability. Reports are available in the terminal, JSON and standalone HTML."
    )
    p(
        "A held-out synthetic evaluation contains 32 scenarios across four device profiles. The full policy records 75% accuracy, 66.67% precision, 66.67% recall and a 20% false positive rate. Authorized backups and stealth activity expose remaining weaknesses. These results demonstrate a working prototype and its limitations; they do not establish real-world compromise detection effectiveness."
    )
    heading("Problem and scope")
    p(
        "The supplied NTRO 2023 software problem statement asks for AI/ML detection of compromise across systems, firewalls, routers and networks, including unknown-IoC situations. Its criteria emphasize rugged detection, cross-device utility, deployment and reporting, and fewer false alarms. ThreatLens addresses those criteria through a reproducible local prototype. Native vendor polling and physical-device security validation remain future work."
    )

    page("Requirements and architecture")
    table(
        ["Criterion", "Implementation evidence", "Limit"],
        [
            [
                "Rugged detection",
                "Robust statistics, source models, persistence and validated state",
                "No privileged-attacker resistance claim",
            ],
            [
                "Device utility",
                "Four device profiles and Zeek export conversion",
                "Router/firewall metrics require an exporter",
            ],
            [
                "Deployment and reporting",
                "Python package, CLI, SQLite, JSON and HTML",
                "No native installer or hosted service",
            ],
            [
                "False alarms",
                "Meaningful-change floors, source consensus and hard benign cases",
                "Legitimate correlated changes still alert",
            ],
        ],
        [1.2, 3.2, 2.15],
    )
    doc.add_picture(str(diagram), width=Inches(6.5))
    p("Figure 1  The deployed behavioral detection path", "Caption")
    heading("Component boundaries")
    p(
        "Typer commands orchestrate validated observations. Collectors and import adapters produce aggregate feature maps. DeviceDetectionService manages learning and temporal state; assess_observation performs inference and is also used by the benchmark. IsolationForestDetector and BehavioralDeviationDetector implement the numerical components. SQLite stores original incident evidence and bounded device state. Reporting reads saved evidence rather than inferring explanations from signal names alone."
    )
    p(
        "The original endpoint pipeline remains as a tested component implementation. The current CLI uses detection/device.py as its common local and imported-device service. There is no Electron window, mandatory web backend or cloud inference dependency."
    )

    page("Telemetry and device coverage")
    table(
        ["Device", "Available source domains", "Current integration"],
        [
            ["System", "System, network, process", "Local sampling or JSON import"],
            ["Router", "System, network, routing", "Exported aggregate JSON metrics"],
            ["Firewall", "System, network, firewall", "Exported aggregate JSON metrics"],
            ["Network", "Network", "JSON or Zeek conn.log TSV"],
        ],
        [1.0, 2.5, 3.05],
    )
    p(
        "Every profile identifies a device and a fixed observation duration. Source maps contain a documented vocabulary of numeric features, such as CPU utilization, process count, connection count, bytes transferred, route changes or denied sessions. Missing sources are declared separately and are never treated as healthy zeros. Raw endpoint strings are not inference signatures."
    )
    code("""{
  "schema_version": 1,
  "device_id": "lab-router",
  "device_type": "router",
  "observations": [{
    "timestamp": "2026-01-01T00:00:00+00:00",
    "window_seconds": 60,
    "sources": {"network": {"bytes_out": 10000}},
    "unavailable": {}
  }]
}""")
    heading("Validation and semantic responsibility")
    p(
        "Imports are bounded to 10 MiB and 1-2000 windows. The parser rejects unknown keys, duplicate JSON fields, invalid IDs, nonfinite or negative metrics, booleans used as numbers, naive timestamps and non-increasing batch times. A scan also rejects timestamps older than the last stored window. Feature names and duration must match the learned profile. Operators remain responsible for truthful metrics, stable units, synchronized clocks and correct sensor identity."
    )
    heading("Zeek mapping")
    p(
        "The Zeek adapter aggregates completed connections into UTC buckets based on start timestamp. It validates address syntax, ports and byte counts, then retains counts and byte totals. Originator bytes map to bytes_out and responder bytes to bytes_in; these labels do not imply local/internet direction. Long-flow totals belong to the start bucket, so this input must not be represented as interface throughput. Missing required Zeek values stop conversion."
    )

    page("Detection method")
    heading("Learning and model construction")
    p(
        "The operator explicitly learns known-normal telemetry. A device needs at least 30 trusted observations and retains at most 500. Every scan uses a frozen baseline; even a single uncorrelated outlier is excluded from automatic learning. This limits silent baseline poisoning but requires reviewed relearning when legitimate workloads change. A readiness flag is not a statistical guarantee that the baseline is representative."
    )
    p(
        "A seeded Isolation Forest is rebuilt for each source using aligned numeric feature names and contamination 0.05. It provides unsupervised outlier evidence. Its decision score is negative for observations beyond its learned anomaly threshold. Contamination controls a threshold offset and is not a compromise probability."
    )
    heading("Robust feature analysis")
    code("m = median(baseline)\nMAD = median(abs(baseline - m))\nz = 0.6745 * (current - m) / MAD")
    p(
        "A feature is anomalous at absolute robust score 3.5 with a meaningful absolute change. The meaningful floor is max(1.0, 10% of the absolute median, 0.000001). Near-zero MAD uses current deviation divided by that floor and requires 3.5 floors of change. Uptime is excluded because elapsed time would otherwise create drift in an uncompromised host."
    )
    heading("Corroboration and temporal evidence")
    p(
        "A source is corroborated when robust deviation triggers and either its Isolation Forest also flags it or an absolute robust score reaches 6. The latter handles extreme changes against nearly constant baselines. An ML-only outlier remains review evidence. A suspicious result needs two corroborated sources in one window or one corroborated source in two comparable consecutive windows."
    )
    p(
        "Comparable windows are separated by at least half the configured duration and at most max(300, five times the duration) seconds. Long gaps reset persistence. The last observed window advances even when suspicious, but never becomes trusted training data. Source domains can share causal behavior; corroboration does not mean statistical independence."
    )
    heading("Investigation priority")
    p(
        "Each corroborated source contributes 25 points, model corroboration adds 10 and persistence adds 20, capped at 100. Review-only evidence scores 10 when no source contribution exists. Severity bands start at 30, 60 and 80. These scores prioritize investigation; they are not probabilities or proof of compromise."
    )

    page("Reliability privacy and incident evidence")
    heading("Evidence lifecycle")
    p(
        "An assessment contains device identity, timestamp, source coverage, feature values, baseline medians, MAD values, robust scores, model scores and risk contributions. A suspicious episode is stored in SQLite with its original explanation. Repeated suspicious windows with the same source set reuse its incident ID. Recovery, changed source evidence or a long observation gap starts a new episode. Current scan output still contains the latest assessment."
    )
    p(
        "An additive database migration preserves original incident IDs and old signal-only records. Evidence that was not saved by version 0.1 cannot be reconstructed later. Legacy automatic-training JSON baselines require explicit relearning under the new profile contract."
    )
    heading("Atomic local state")
    p(
        "Scan and learning batches use SQLite writer transactions. If a later imported window is replayed or invalid, preceding updates in that batch roll back with its incident inserts. Connections close after each operation. This prevents partially applied local state; it is not a distributed event store or a tamper-evident forensic record."
    )
    heading("Collection quality")
    p(
        "CPU is measured over an interval. Process CPU is primed before measurement, avoiding meaningless first-call zeros. Inaccessible or exiting processes make that source conservatively unavailable. Denied network access is reported as unavailable rather than empty activity. The operator can deliberately select a narrower local source profile; its complete status applies only to that trained profile."
    )
    heading("Privacy and remaining trust assumptions")
    p(
        "Inference is local. The current service stores aggregate features instead of raw process tables and endpoint identities. New database and exported files use private POSIX permissions; reports refuse to overwrite existing files or symlinks. HTML evidence is escaped and the report uses a restrictive content security policy without external scripts. Windows protection follows account ACLs. Existing file permissions are retained."
    )
    p(
        "There is no encryption, authenticated sensor identity, remote replication or privileged telemetry-tamper protection. A compromised OS, poisoned initial baseline or dishonest exporter can undermine results. ThreatLens does not block traffic, terminate processes or modify device configuration. All alerts require contextual verification."
    )

    page("Evaluation design and results")
    p(
        "The default benchmark calls the deployed assessment function. Each of four profiles has 60 separately generated training windows and eight held-out scenarios. Training remains frozen. State resets between scenarios and advances within each scenario. A scenario is predicted positive if any of its windows alerts. Fixed seed 42 supports reproduction, not generalization to arbitrary networks."
    )
    table(
        ["Scenario group", "Intended label", "Purpose"],
        [
            ["Normal and benign jitter", "Benign", "Check ordinary variation"],
            ["Transient transfer and recovery", "Benign", "Check persistence policy"],
            ["Sustained transfer and multiple sources", "Simulated compromise", "Check escalation"],
            ["Authorized backup", "Benign", "Expose a hard false alarm"],
            ["Stealth behavior near normal", "Simulated compromise", "Expose a blind spot"],
        ],
        [2.4, 1.5, 2.65],
    )
    m = benchmark["metrics"]
    table(
        ["Method", "Precision", "Recall", "F1", "FPR"],
        [
            [
                "Full detector",
                f"{m['precision']:.2%}",
                f"{m['recall']:.2%}",
                f"{m['f1']:.2%}",
                f"{m['false_positive_rate']:.2%}",
            ],
            ["Isolation Forest only", "40.00%", "66.67%", "50.00%", "60.00%"],
            ["Robust statistics only", "40.00%", "66.67%", "50.00%", "60.00%"],
        ],
        [2.2, 1.1, 1.1, 1.05, 1.0],
    )
    table(
        ["Ground truth", "Predicted suspicious", "Predicted not suspicious"],
        [
            ["Simulated compromise", m["true_positive"], m["false_negative"]],
            ["Simulated benign", m["false_positive"], m["true_negative"]],
        ],
        [2.3, 2.1, 2.15],
    )
    p(
        "Accuracy is 75%. Each profile produces TP 2, TN 4, FP 1 and FN 1. A sustained single-source anomaly alerts in its second comparable window. Ablations classify any flagged source/window as positive, so the comparison demonstrates this synthetic decision policy rather than empirical superiority in real devices."
    )
    p(
        "The profiles repeat scenario patterns; they are not independent real-world samples. Authorized and malicious transfers can have identical metrics. No labeled compromised-device dataset or physical-router/firewall experiment was performed. The 20% synthetic FPR is not an operational estimate and the 66.67% recall must not be presented as a guaranteed security detection rate."
    )

    page("Engineering verification")
    table(
        ["Check", "Recorded result"],
        [
            [
                "Automated tests",
                f"{validation['tests_passed']} passed on local macOS / Python 3.14.3",
            ],
            [
                "Branch-aware coverage",
                f"{validation['coverage_percent']:.1f}% of measured source and branches",
            ],
            ["Static checks", "Ruff lint and formatting passed; source compiled"],
            [
                "Packaging",
                "Wheel and source archive built; installed CLI checked outside source tree",
            ],
            ["End-to-end demo", "Four profiles learn, assess and generate saved evidence reports"],
            ["Dependency audit", "No known vulnerabilities after isolated pip update"],
            [
                "Cross-platform CI",
                "Linux, macOS, Windows on Python 3.11 and 3.14; package job passed",
            ],
            [
                "Container execution",
                validation["docker"],
            ],
        ],
        [1.8, 4.75],
    )
    heading("Regression coverage")
    p(
        "Tests cover identity and schema validation, finite metrics, uptime drift, missing features, tiny-variance behavior, collector denial, process CPU sampling, per-device isolation, trusted learning, frozen baselines, previous-window advancement, persistence and gap resets. They also verify episode grouping, replay rejection, atomic rollback, SQLite migration, original evidence recovery, output permissions, symlink protection, report escaping, CLI errors and complete CLI workflows."
    )
    p(
        "Host unit tests use controlled telemetry instead of the developer's real workload. A separate installed-app smoke collection successfully exported aggregate system metrics from the actual local host. That check verifies the adapter's execution; it does not establish that the host is uncompromised."
    )
    heading("Validation provenance")
    p(
        "The machine-readable benchmark and validation summaries accompany the submission. The repository's validation record distinguishes local execution from GitHub CI and identifies what was not tested. Engineering checks establish behavior under defined inputs; they do not replace independent security ground truth."
    )
    p(
        "A reproducible dependency lock is included for uv. Regular pip installations resolve within declared compatible ranges. No public PyPI publication, native installer signing or app-store submission was performed."
    )

    page("Demonstration deployment and future work")
    heading("Reproduce the demonstration")
    code(
        'python -m pip install ".[dev]"\npython scripts/demo.py --output demo-artifacts\npython -m threatlens benchmark --json\npython -m pytest -q\npython -m build'
    )
    p(
        "The demo uses generated fixtures and its own state directory. It learns each profile, checks benign telemetry, assesses a sustained anomaly and exports scan JSON, an incident HTML report and a benchmark result. Use a new output directory for a repeat run. To inspect the same database manually, point THREATLENS_DATA_DIR at the demo's state subdirectory."
    )
    heading("Deployment boundary")
    p(
        "The wheel installs into a compatible Python environment and exposes the threatlens command. It still needs platform-specific dependencies. A container runs with a non-root account and state under /data, but observes its configured namespaces; it does not automatically inspect the host or a physical router. Native executables, signed installers and public distribution are separate release tasks. The repository retains its original all-rights-reserved license."
    )
    heading("Next research steps")
    p(
        "Collect representative trusted telemetry over normal workload modes, obtain independently verified attack labels, and reserve held-out devices and later time periods. Freeze thresholds before testing. Measure per-device false alarms, precision/recall, onset-to-alert delay and CPU/memory overhead. Add authenticated vendor exporters and independent evidence sources before asserting infrastructure-wide utility. Review legitimate drift explicitly instead of quietly retraining during attacks."
    )
    heading("Conclusion")
    p(
        "ThreatLens provides a working and explainable non-IoC behavioral workflow with bounded trusted state, multiple device contracts, evidence reporting and reproducible engineering checks. Its strongest submission claim is that the implementation and its limitations can be demonstrated clearly. It cannot prove compromise from aggregate anomalies alone."
    )
    heading("References and project material")
    for text in (
        "Project source and documentation: github.com/samiksha-jangid27/ThreatLens-CLI",
        "scikit-learn Isolation Forest API: scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html",
        "psutil API and CPU sampling guidance: psutil.readthedocs.io/stable/",
        "Zeek connection log reference: docs.zeek.org/en/current/reference/logs/conn.html",
        "Assignment source: NTRO 2023 problem statement supplied for the class project.",
    ):
        paragraph = p(text)
        for run in paragraph.runs:
            run.font.size = Pt(9)
    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=Path("docs/submission/benchmark.json"))
    parser.add_argument("--validation", type=Path, default=Path("docs/submission/validation.json"))
    parser.add_argument("--diagram", type=Path, default=Path("docs/assets/architecture.png"))
    parser.add_argument(
        "--output", type=Path, default=Path("docs/submission/ThreatLens-Project-Report.docx")
    )
    args = parser.parse_args()
    build(
        json.loads(args.benchmark.read_text()),
        json.loads(args.validation.read_text()),
        args.diagram,
        args.output,
    )
