from __future__ import annotations

from typing import Any, Literal, TypedDict

ApplySource = Literal["INPUT", "OUTPUT"]
OutputScope = Literal["INTERVENTIONS", "FULL"]
ApplyAction = Literal["NONE", "GUARDRAIL_INTERVENED"]


class ContentText(TypedDict, total=False):
    text: str
    qualifiers: Literal["yang_open_guardrails"]


class ContentBlock(TypedDict):
    text: ContentText


class ApplyOutput(TypedDict, total=False):
    text: str


class ApplyProfile(TypedDict, total=False):
    id: str
    version: str
    versionId: str


class ApplyWarning(TypedDict, total=False):
    code: str
    policy: str
    message: str


class ApplyResult(TypedDict, total=False):
    requestId: str
    profile: ApplyProfile
    action: ApplyAction
    actionReason: str
    outputs: list[ApplyOutput]
    assessments: list[dict[str, Any]]
    usage: dict[str, Any]
    guardrailCoverage: dict[str, Any]
    degraded: bool
    warnings: list[ApplyWarning]
