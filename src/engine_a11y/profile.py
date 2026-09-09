"""Comprehensive WCAG Criteria Catalog and Document Accessibility Profiles.

Provides complete WCAG Level A/AA coverage matrices and allows each format-specific
audit tool to explicitly declare automated checks, human-in-the-loop review items,
and unchecked/not-applicable criteria with clear annotations. Also supports user-defined
what-if exclusions.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from .findings import Finding

W3C_UNDERSTANDING = "https://www.w3.org/WAI/WCAG21/Understanding/"


class SCStatus(str, Enum):
    PASS = "PASS"                          # Automated check ran; 0 findings
    FAIL = "FAIL"                          # Automated check ran; 1+ findings detected
    MANUAL_REVIEW = "MANUAL_REVIEW"        # Human-in-the-loop inspection required
    UNCHECKED = "UNCHECKED"                # In scope for a11y, but unchecked by this tool
    NOT_APPLICABLE = "NOT_APPLICABLE"      # Not applicable to this file format


# Complete Catalog of WCAG 2.1 / 2.2 Level A & AA Success Criteria
WCAG_CATALOG: Dict[str, Dict[str, str]] = {
    # Principle 1: Perceivable
    "1.1.1": {"principle": "1", "level": "A", "title": "Non-text Content", "slug": "non-text-content"},
    "1.2.1": {"principle": "1", "level": "A", "title": "Audio-only and Video-only (Prerecorded)", "slug": "audio-only-and-video-only-prerecorded"},
    "1.2.2": {"principle": "1", "level": "A", "title": "Captions (Prerecorded)", "slug": "captions-prerecorded"},
    "1.2.3": {"principle": "1", "level": "A", "title": "Audio Description or Media Alternative (Prerecorded)", "slug": "audio-description-or-media-alternative-prerecorded"},
    "1.2.4": {"principle": "1", "level": "AA", "title": "Captions (Live)", "slug": "captions-live"},
    "1.2.5": {"principle": "1", "level": "AA", "title": "Audio Description (Prerecorded)", "slug": "audio-description-prerecorded"},
    "1.3.1": {"principle": "1", "level": "A", "title": "Info and Relationships", "slug": "info-and-relationships"},
    "1.3.2": {"principle": "1", "level": "A", "title": "Meaningful Sequence", "slug": "meaningful-sequence"},
    "1.3.3": {"principle": "1", "level": "A", "title": "Sensory Characteristics", "slug": "sensory-characteristics"},
    "1.3.4": {"principle": "1", "level": "AA", "title": "Orientation", "slug": "orientation"},
    "1.3.5": {"principle": "1", "level": "AA", "title": "Identify Input Purpose", "slug": "identify-input-purpose"},
    "1.4.1": {"principle": "1", "level": "A", "title": "Use of Color", "slug": "use-of-color"},
    "1.4.2": {"principle": "1", "level": "A", "title": "Audio Control", "slug": "audio-control"},
    "1.4.3": {"principle": "1", "level": "AA", "title": "Contrast (Minimum)", "slug": "contrast-minimum"},
    "1.4.4": {"principle": "1", "level": "AA", "title": "Resize Text", "slug": "resize-text"},
    "1.4.5": {"principle": "1", "level": "AA", "title": "Images of Text", "slug": "images-of-text"},
    "1.4.10": {"principle": "1", "level": "AA", "title": "Reflow", "slug": "reflow"},
    "1.4.11": {"principle": "1", "level": "AA", "title": "Non-text Contrast", "slug": "non-text-contrast"},
    "1.4.12": {"principle": "1", "level": "AA", "title": "Text Spacing", "slug": "text-spacing"},
    "1.4.13": {"principle": "1", "level": "AA", "title": "Content on Hover or Focus", "slug": "content-on-hover-or-focus"},

    # Principle 2: Operable
    "2.1.1": {"principle": "2", "level": "A", "title": "Keyboard", "slug": "keyboard"},
    "2.1.2": {"principle": "2", "level": "A", "title": "No Keyboard Trap", "slug": "no-keyboard-trap"},
    "2.1.4": {"principle": "2", "level": "A", "title": "Character Key Shortcuts", "slug": "character-key-shortcuts"},
    "2.2.1": {"principle": "2", "level": "A", "title": "Timing Adjustable", "slug": "timing-adjustable"},
    "2.2.2": {"principle": "2", "level": "A", "title": "Pause, Stop, Hide", "slug": "pause-stop-hide"},
    "2.3.1": {"principle": "2", "level": "A", "title": "Three Flashes or Below Threshold", "slug": "three-flashes-or-below-threshold"},
    "2.4.1": {"principle": "2", "level": "A", "title": "Bypass Blocks", "slug": "bypass-blocks"},
    "2.4.2": {"principle": "2", "level": "A", "title": "Page Titled", "slug": "page-titled"},
    "2.4.3": {"principle": "2", "level": "A", "title": "Focus Order", "slug": "focus-order"},
    "2.4.4": {"principle": "2", "level": "A", "title": "Link Purpose (In Context)", "slug": "link-purpose-in-context"},
    "2.4.5": {"principle": "2", "level": "AA", "title": "Multiple Ways", "slug": "multiple-ways"},
    "2.4.6": {"principle": "2", "level": "AA", "title": "Headings and Labels", "slug": "headings-and-labels"},
    "2.4.7": {"principle": "2", "level": "AA", "title": "Focus Visible", "slug": "focus-visible"},
    "2.5.1": {"principle": "2", "level": "A", "title": "Pointer Gestures", "slug": "pointer-gestures"},
    "2.5.2": {"principle": "2", "level": "A", "title": "Pointer Cancellation", "slug": "pointer-cancellation"},
    "2.5.3": {"principle": "2", "level": "A", "title": "Label in Name", "slug": "label-in-name"},
    "2.5.4": {"principle": "2", "level": "A", "title": "Motion Actuation", "slug": "motion-actuation"},
    "2.5.7": {"principle": "2", "level": "AA", "title": "Dragging Movements", "slug": "dragging-movements"},
    "2.5.8": {"principle": "2", "level": "AA", "title": "Target Size (Minimum)", "slug": "target-size-minimum"},

    # Principle 3: Understandable
    "3.1.1": {"principle": "3", "level": "A", "title": "Language of Page", "slug": "language-of-page"},
    "3.1.2": {"principle": "3", "level": "AA", "title": "Language of Parts", "slug": "language-of-parts"},
    "3.2.1": {"principle": "3", "level": "A", "title": "On Focus", "slug": "on-focus"},
    "3.2.2": {"principle": "3", "level": "A", "title": "On Input", "slug": "on-input"},
    "3.2.3": {"principle": "3", "level": "AA", "title": "Consistent Navigation", "slug": "consistent-navigation"},
    "3.2.4": {"principle": "3", "level": "AA", "title": "Consistent Identification", "slug": "consistent-identification"},
    "3.3.1": {"principle": "3", "level": "A", "title": "Error Identification", "slug": "error-identification"},
    "3.3.2": {"principle": "3", "level": "A", "title": "Labels or Instructions", "slug": "labels-or-instructions"},
    "3.3.3": {"principle": "3", "level": "AA", "title": "Error Suggestion", "slug": "error-suggestion"},
    "3.3.4": {"principle": "3", "level": "AA", "title": "Error Prevention (Legal, Financial, Data)", "slug": "error-prevention-legal-financial-data"},
    "3.3.7": {"principle": "3", "level": "A", "title": "Redundant Entry", "slug": "redundant-entry"},
    "3.3.8": {"principle": "3", "level": "AA", "title": "Accessible Authentication (Minimum)", "slug": "accessible-authentication-minimum"},

    # Principle 4: Robust
    "4.1.1": {"principle": "4", "level": "A", "title": "Parsing", "slug": "parsing"},
    "4.1.2": {"principle": "4", "level": "A", "title": "Name, Role, Value", "slug": "name-role-value"},
    "4.1.3": {"principle": "4", "level": "AA", "title": "Status Messages", "slug": "status-messages"},
}


def get_complete_wcag_catalog() -> Dict[str, Dict[str, str]]:
    """Return dictionary of all WCAG Level A & AA Success Criteria."""
    return WCAG_CATALOG


@dataclass
class DocumentProfile:
    """Declares format-specific WCAG conformance evaluation capabilities."""

    name: str = "Document"
    doc_type: str = "Document"
    automated_sc: Dict[str, str] = field(default_factory=dict)
    human_in_the_loop_sc: Dict[str, str] = field(default_factory=dict)
    not_applicable_sc: Dict[str, str] = field(default_factory=dict)
    unchecked_sc: Dict[str, str] = field(default_factory=dict)


def evaluate_sc_matrix(
    findings: List[Finding],
    profile: Optional[DocumentProfile] = None,
    excluded_sc: Optional[Set[str]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Generate exhaustive status mapping for all WCAG criteria, noting user exclusions."""
    p = profile or DocumentProfile()
    excluded = excluded_sc or set()
    findings_by_sc: Dict[str, List[Finding]] = {}
    for f in findings:
        findings_by_sc.setdefault(f.sc, []).append(f)

    matrix: Dict[str, Dict[str, Any]] = {}

    for sc, meta in WCAG_CATALOG.items():
        title = meta["title"]
        level = meta["level"]
        principle = meta["principle"]
        url = f"{W3C_UNDERSTANDING}{meta['slug']}.html"

        sc_findings = findings_by_sc.get(sc, [])
        is_user_excluded = sc in excluded

        if sc in p.automated_sc:
            if sc_findings:
                status = SCStatus.FAIL
                prefix = "[EXCLUDED FROM SUMMARY] " if is_user_excluded else ""
                annotation = f"{prefix}Automated check detected {len(sc_findings)} barrier(s): {p.automated_sc[sc]}"
            else:
                status = SCStatus.PASS
                prefix = "[EXCLUDED FROM SUMMARY] " if is_user_excluded else ""
                annotation = f"{prefix}Automated check passed: {p.automated_sc[sc]}"
        elif sc in p.human_in_the_loop_sc:
            status = SCStatus.MANUAL_REVIEW
            annotation = p.human_in_the_loop_sc[sc]
        elif sc in p.not_applicable_sc:
            status = SCStatus.NOT_APPLICABLE
            annotation = p.not_applicable_sc[sc]
        elif sc in p.unchecked_sc:
            status = SCStatus.UNCHECKED
            annotation = p.unchecked_sc[sc]
        else:
            if sc_findings:
                status = SCStatus.FAIL
                annotation = f"Detected {len(sc_findings)} finding(s)."
            else:
                status = SCStatus.UNCHECKED
                annotation = "Not evaluated by this automated tool."

        if is_user_excluded:
            annotation += " (Excluded from compliance score via user criteria configuration)"

        matrix[sc] = {
            "sc": sc,
            "title": title,
            "level": level,
            "principle": principle,
            "url": url,
            "status": status,
            "annotation": annotation,
            "findings": sc_findings,
            "is_excluded": is_user_excluded,
        }

    return matrix


def get_docx_profile() -> DocumentProfile:
    """Return canonical accessibility conformance profile for Word .docx documents."""
    return DocumentProfile(
        name="Word Document (DOCX)",
        doc_type="Document",
        automated_sc={
            "1.1.1": "Evaluates alternative text attributes on inline and anchored pictures.",
            "1.3.1": "Validates heading hierarchy (H1-H6) and header rows on data tables.",
            "1.4.3": "Calculates contrast ratio of run font colors against shading and highlights.",
            "2.4.2": "Checks core.xml document title property.",
            "2.4.4": "Detects raw URLs and non-descriptive hyperlink text.",
            "3.1.1": "Checks document default language tag.",
        },
        human_in_the_loop_sc={
            "1.1.1": "Human reviewer must verify that alternative text meaningfully describes the image intent.",
            "1.3.2": "Verify reading flow across multi-column text frames and floating tables.",
            "1.4.1": "Ensure information conveyed by colored text is also denoted with text or iconography.",
            "2.4.6": "Ensure headings and section titles accurately describe subsequent topic sections.",
        },
        not_applicable_sc={
            "1.2.1": "Audio-only and video-only prerecorded media are not embedded in static text documents.",
            "1.2.2": "Captions for synchronized media are not applicable to Word documents without video.",
            "1.2.3": "Audio descriptions are not applicable to Word documents without video.",
            "1.2.4": "Live captions do not apply to static files.",
            "1.2.5": "Prerecorded audio descriptions do not apply to static documents.",
            "1.4.2": "Audio controls do not apply to non-audio document files.",
            "2.1.4": "Character key shortcuts are controlled by Microsoft Word or assistive tech, not document author.",
            "2.5.1": "Pointer gestures are dictated by the document reader software.",
            "2.5.4": "Motion actuation is not supported in document files.",
        },
        unchecked_sc={
            "1.4.10": "Reflow behavior depends on the target word processor window size and page view.",
            "1.4.12": "Text spacing custom overrides are applied dynamically by the reading client.",
            "2.1.1": "Keyboard navigation is handled by the word processing host application.",
            "2.1.2": "Focus trapping is managed by the host application.",
            "2.4.7": "Focus visibility is managed by the reader application.",
        },
    )


def get_pptx_profile() -> DocumentProfile:
    """Return canonical accessibility conformance profile for PowerPoint .pptx presentations."""
    return DocumentProfile(
        name="PowerPoint Presentation (PPTX)",
        doc_type="Presentation",
        automated_sc={
            "1.1.1": "Checks alternative text on shapes, pictures, and SmartArt graphics.",
            "1.3.1": "Validates slide titles, section names, and table header rows.",
            "1.3.2": "Audits slide reading order sequence via z-order/selection pane traversal.",
            "1.4.3": "Calculates contrast between shape text and shape/slide background fills.",
            "2.4.2": "Validates unique slide titles and document title property.",
            "2.4.4": "Audits descriptive link text on slide hyperlinks.",
        },
        human_in_the_loop_sc={
            "1.1.1": "Verify alt text accurately conveys the educational or communicative message of complex diagrams.",
            "1.3.2": "Review reading order to confirm speech synthesis flows naturally through slide elements.",
            "1.4.1": "Ensure chart legends and data series do not rely solely on color differences.",
            "2.4.6": "Confirm slide titles are descriptive and distinct across consecutive slides.",
        },
        not_applicable_sc={
            "1.4.10": "Reflow does not apply to fixed-aspect ratio slide presentation canvases.",
            "1.4.2": "Audio controls do not apply to presentations without embedded sound clips.",
            "2.1.4": "Character key shortcuts are managed by PowerPoint application.",
            "2.5.1": "Pointer gestures are dictated by the presentation reader.",
        },
        unchecked_sc={
            "1.2.2": "Captions for embedded video media must be inspected manually in authoring software.",
            "2.1.1": "Keyboard navigation across slide elements is managed by the presentation runner.",
            "2.4.7": "Focus visibility during slideshow mode is controlled by the application.",
        },
    )


def get_xlsx_profile() -> DocumentProfile:
    """Return canonical accessibility conformance profile for Excel .xlsx workbooks."""
    return DocumentProfile(
        name="Excel Workbook (XLSX)",
        doc_type="Workbook",
        automated_sc={
            "1.1.1": "Audits alt text on embedded charts, drawings, and images.",
            "1.3.1": "Checks default sheet names, merged cell violations, and defined table header rows.",
            "1.4.3": "Evaluates contrast ratio between cell font color and cell fill color.",
            "2.4.2": "Checks workbook title metadata in core.xml.",
            "2.4.4": "Audits HYPERLINK formula labels and cell link descriptions.",
        },
        human_in_the_loop_sc={
            "1.3.1": "Review multi-dimensional financial tables for clear row/column relationships.",
            "1.4.1": "Verify that cell highlights (e.g. green/red status) include text indicators or badges.",
            "2.4.6": "Confirm column and table headers accurately describe cell contents.",
        },
        not_applicable_sc={
            "1.2.1": "Time-based audio/video media is not applicable to spreadsheet data sheets.",
            "1.2.2": "Captions do not apply to spreadsheets.",
            "1.4.10": "Reflow does not apply to fixed grid spreadsheets.",
            "2.1.4": "Character key shortcuts are handled by Excel software.",
        },
        unchecked_sc={
            "2.1.1": "Grid cell keyboard navigation is implemented by spreadsheet software.",
            "2.4.7": "Cell cursor focus visibility is controlled by the spreadsheet application.",
        },
    )


def get_pdf_profile() -> DocumentProfile:
    """Return canonical accessibility conformance profile for PDF documents."""
    return DocumentProfile(
        name="PDF Document (PDF/UA)",
        doc_type="PDF",
        automated_sc={
            "1.1.1": "Audits /Figure tags for presence of /Alt attributes and /Artifact markings.",
            "1.3.1": "Validates /StructTreeRoot, heading hierarchy (/H1-/H6), /Table, /TR, /TH, /TD.",
            "1.4.3": "Audits text rendering contrast against bounding box background color.",
            "2.4.2": "Checks /ViewerPreferences << /DisplayDocTitle true >> and /dc:title metadata.",
            "2.4.4": "Checks /Link annotations for descriptive /Contents or /Alt text.",
            "3.1.1": "Checks /Root /Lang catalog language identifier.",
            "4.1.2": "Checks /MarkInfo << /Marked true >> and accessibility tag tree integrity.",
        },
        human_in_the_loop_sc={
            "1.1.1": "Human auditor must verify that Figure /Alt text provides appropriate semantic context.",
            "1.3.2": "Verify tag tree reading order (/StructTreeRoot) matches logical reading order.",
            "1.4.1": "Verify color is not used as the sole means of conveying information in figures.",
            "2.4.6": "Confirm bookmarks and outline tree provide descriptive section labels.",
        },
        not_applicable_sc={
            "1.2.1": "Audio/video prerecorded media is not applicable to static PDF documents.",
            "1.4.2": "Audio controls do not apply to documents without audio streams.",
            "2.1.4": "Shortcuts are handled by PDF viewer (Acrobat, Preview).",
            "2.5.1": "Gestures are handled by PDF viewer.",
        },
        unchecked_sc={
            "1.4.10": "Reflow depends on PDF reader reflow capabilities and tag tagging quality.",
            "2.1.1": "Keyboard tab order through interactive links and form fields is handled by PDF viewer.",
            "2.4.7": "Focus indication is handled by the PDF viewer.",
        },
    )
