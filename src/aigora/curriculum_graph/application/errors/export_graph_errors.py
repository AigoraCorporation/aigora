from __future__ import annotations


class ExportGraphError(Exception):
    """Base exception for export graph use case errors."""


class UnsupportedCurriculumGraphExportFormatError(ExportGraphError, ValueError):
    """Raised when no export strategy is registered for the requested format."""
