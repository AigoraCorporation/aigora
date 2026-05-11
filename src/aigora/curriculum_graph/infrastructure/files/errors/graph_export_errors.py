from __future__ import annotations


class CurriculumGraphFileExportError(Exception):
    """Base exception for file-based CurriculumGraph export failures."""


class CurriculumGraphCsvExporterError(CurriculumGraphFileExportError):
    """Raised when CurriculumGraph CSV export fails."""


class CurriculumGraphJsonExporterError(CurriculumGraphFileExportError):
    """Raised when CurriculumGraph JSON export fails."""


class CurriculumGraphYamlExporterError(CurriculumGraphFileExportError):
    """Raised when CurriculumGraph YAML export fails."""
