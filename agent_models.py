# agent_models.py

from typing import List

from pydantic import BaseModel, Field


class FormattingResult(BaseModel):
    total_subtitles: int = Field(..., description="Total number of formatted subtitles")
    first_subtitle: dict = Field(..., description="The first formatted subtitle")
    last_subtitle: dict = Field(..., description="The last formatted subtitle")
    warnings: List[str] = Field(
        default_factory=list,
        description="List of warnings for subtitles exceeding limits",
    )


class WiktionaryDefinition(BaseModel):
    word: str
    definition: str
    language: str


class WiktionaryResult(BaseModel):
    definitions: List[WiktionaryDefinition] = Field(default_factory=list)
    not_found: List[str] = Field(default_factory=list)


class AlignmentResult(BaseModel):
    is_aligned: bool
    misaligned_indices: List[int] = Field(default_factory=list)
