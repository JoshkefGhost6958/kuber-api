from pricing.models import DocumentRequirement


def _active_vehicle_type_code(driver):
    v = driver.vehicles.filter(is_active=True).first()
    return v.vehicle_type.code if v else None


def build_checklist(driver):
    """Required docs for the driver's active vehicle type, with current status.

    status is the ComplianceDocument status, or "MISSING" if not yet uploaded.
    """
    code = _active_vehicle_type_code(driver)
    reqs = DocumentRequirement.objects.filter(vehicle_type__code=code)
    docs = {d.doc_type: d.status for d in driver.documents.all()}
    return [
        {
            "doc_type": r.doc_type,
            "is_mandatory": r.is_mandatory,
            "status": docs.get(r.doc_type, "MISSING"),
        }
        for r in reqs
    ]


def is_driver_approvable(driver) -> bool:
    items = build_checklist(driver)
    if not items:
        return False
    return all(i["status"] == "APPROVED" for i in items if i["is_mandatory"])


def missing_mandatory(driver) -> list[str]:
    return [
        i["doc_type"]
        for i in build_checklist(driver)
        if i["is_mandatory"] and i["status"] == "MISSING"
    ]
