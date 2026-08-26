"""Per-component runtime inspection.

See docs/bible/16-geometry-inspection/464-component-inspection-contract.md.
Every current solitaire component (band, stone_reference, prongs,
basket_support) is inspected the same way — no component-specific
special-casing beyond what its own real `GeneratedComponent.warnings`/
`metadata` already record (e.g. band's `filletApplied`, prongs'
`requestedCount`/`generatedCount`).
"""

from __future__ import annotations

from jewelmind.geometry.inspection.models import ComponentInspectionResult, InspectionDiagnostic
from jewelmind.geometry.inspection.shape import bounding_box_fact
from jewelmind.geometry.inspection.topology import inspect_topology
from jewelmind.geometry.model import GeneratedComponent


def inspect_component(name: str, component: GeneratedComponent) -> ComponentInspectionResult:
    diagnostics: list[InspectionDiagnostic] = []
    shape = component.shape
    exists = bool(shape.Solids())

    if not exists:
        return ComponentInspectionResult(
            componentId=name,
            exists=False,
            status="FAIL",
            solidCount=0,
            volumeMm3=0.0,
            fallbackUsed=bool(component.warnings),
            metadata=dict(component.metadata),
            diagnostics=[
                InspectionDiagnostic(
                    code="INSPECTION_COMPONENT_MISSING",
                    severity="warning",
                    message=f"Component '{name}' generated no solids.",
                    componentIds=[name],
                )
            ],
        )

    try:
        bbox = bounding_box_fact(shape)
    except Exception:  # noqa: BLE001 - a kernel bounding-box failure must not crash the pipeline
        bbox = None
        diagnostics.append(
            InspectionDiagnostic(
                code="INSPECTION_BOUNDING_BOX_FAILED",
                severity="error",
                message=f"Bounding box computation failed for component '{name}'.",
                componentIds=[name],
            )
        )

    counts, valid, topology_status = inspect_topology(shape)
    if topology_status == "ERROR":
        diagnostics.append(
            InspectionDiagnostic(
                code="INSPECTION_TOPOLOGY_FAILED",
                severity="error",
                message=f"Topology inspection failed for component '{name}'.",
                componentIds=[name],
            )
        )

    volume = component.volume_mm3
    volume_ok = volume is not None and volume >= 0.0 and volume == volume  # NaN check via self-equality
    if not volume_ok:
        diagnostics.append(
            InspectionDiagnostic(
                code="INSPECTION_VOLUME_FAILED",
                severity="error",
                message=f"Component '{name}' reported a non-finite or negative volume.",
                componentIds=[name],
            )
        )

    status = "FAIL" if any(d.severity == "error" for d in diagnostics) else "PASS"

    return ComponentInspectionResult(
        componentId=name,
        exists=True,
        status=status,
        shapeType=shape.ShapeType() if hasattr(shape, "ShapeType") else None,
        solidCount=counts.solids if counts else None,
        volumeMm3=volume,
        boundingBox=bbox,
        topology=counts,
        shapeValid=valid,
        fallbackUsed=bool(component.warnings),
        metadata=dict(component.metadata),
        diagnostics=diagnostics,
    )
