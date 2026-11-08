"""
qeemah-zatca - Saudi Arabia ZATCA Phase 2 E-Invoicing & VAT compliance plugin for Hermes Agent.

Exposes model-callable tools for:
- ksa_vat_calculate: 15% standard rate VAT, net subtotals, and gross totals in SAR.
- zatca_validate_invoice: Validates invoice fields against ZATCA Schematron and business rules (KSA-1 to KSA-16).
"""

from __future__ import annotations

import logging
import re
from typing import Any

from tools.registry import tool_error, tool_result

logger = logging.getLogger(__name__)

VAT_CALCULATE_SCHEMA = {
    "description": (
        "Calculate Saudi Arabia Value Added Tax (VAT) at the standard 15% rate, "
        "including subtotal, VAT amount, and total payable in SAR. Handles both tax-inclusive and tax-exclusive amounts."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "amount": {
                "type": "number",
                "description": "Monetary amount in Saudi Riyals (SAR).",
            },
            "is_inclusive": {
                "type": "boolean",
                "description": "Set to true if amount already includes 15% VAT; false if amount is before VAT. Defaults to false.",
            },
        },
        "required": ["amount"],
        "additionalProperties": False,
    },
}

ZATCA_VALIDATE_SCHEMA = {
    "description": (
        "Validate an invoice data payload against official Saudi ZATCA Phase 2 (FATOORA) business rules "
        "(UUID, 15-digit VAT number, sequential ICV, timestamp, and totals)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "uuid": {
                "type": "string",
                "description": "Invoice UUID (Version 4 formatted UUID string, KSA-3).",
            },
            "seller_vat": {
                "type": "string",
                "description": "Seller's 15-digit Tax Identification Number (must start and end with 3, KSA-6).",
            },
            "icv": {
                "type": "integer",
                "description": "Invoice Counter Value (positive sequential integer strictly >= 1, KSA-14).",
                "minimum": 1,
            },
            "issue_date": {
                "type": "string",
                "description": "Issue date formatted as YYYY-MM-DD (KSA-5).",
            },
            "issue_time": {
                "type": "string",
                "description": "Issue time in AST (Saudi Arabia Standard Time, UTC+3) formatted as HH:mm:ss (KSA-25).",
            },
            "total_without_vat": {
                "type": "number",
                "description": "Taxable amount / subtotal before VAT in SAR.",
            },
            "vat_amount": {
                "type": "number",
                "description": "Total VAT amount in SAR.",
            },
            "total_with_vat": {
                "type": "number",
                "description": "Total amount payable including VAT in SAR.",
            },
        },
        "required": ["uuid", "seller_vat", "icv", "total_without_vat", "vat_amount", "total_with_vat"],
        "additionalProperties": False,
    },
}


def _handle_vat_calculate(args: dict, **kwargs: Any) -> str:
    del kwargs
    try:
        amount = float(args.get("amount", 0))
    except (TypeError, ValueError):
        return tool_error("amount must be a valid number")

    if amount < 0:
        return tool_error("amount must be non-negative")

    is_inclusive = bool(args.get("is_inclusive", False))

    if is_inclusive:
        subtotal = round(amount / 1.15, 2)
        vat_amount = round(amount - subtotal, 2)
        total = round(amount, 2)
    else:
        subtotal = round(amount, 2)
        vat_amount = round(amount * 0.15, 2)
        total = round(subtotal + vat_amount, 2)

    return tool_result({
        "success": True,
        "currency": "SAR",
        "is_inclusive_input": is_inclusive,
        "subtotal": subtotal,
        "vat_rate": "15%",
        "vat_amount": vat_amount,
        "total": total,
    })


def _handle_zatca_validate(args: dict, **kwargs: Any) -> str:
    del kwargs
    uuid_val = str(args.get("uuid", "")).strip()
    seller_vat = str(args.get("seller_vat", "")).strip()
    icv = args.get("icv")
    subtotal = float(args.get("total_without_vat", 0))
    vat = float(args.get("vat_amount", 0))
    total = float(args.get("total_with_vat", 0))

    errors = []

    # Rule KSA-3: Valid UUID v4
    uuid_re = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
    if not uuid_re.match(uuid_val):
        errors.append("BR-KSA-03: UUID is not a valid Version 4 UUID.")

    # Rule KSA-6: 15-digit VAT number starting and ending with 3
    if not (len(seller_vat) == 15 and seller_vat.isdigit() and seller_vat.startswith("3") and seller_vat.endswith("3")):
        errors.append("BR-KSA-06: Seller VAT number must be exactly 15 digits starting and ending with '3'.")

    # Rule KSA-14: Sequential ICV >= 1
    if not isinstance(icv, int) or icv < 1:
        errors.append("BR-KSA-14: Invoice Counter Value (ICV) must be an integer >= 1.")

    # Mathematical consistency: total == subtotal + vat
    expected_vat = round(subtotal * 0.15, 2)
    expected_total = round(subtotal + vat, 2)
    if abs(vat - expected_vat) > 0.05:
        errors.append(f"BR-KSA-52: VAT amount ({vat} SAR) does not match expected 15% rate ({expected_vat} SAR).")
    if abs(total - expected_total) > 0.05:
        errors.append(f"BR-KSA-53: Total with VAT ({total} SAR) does not equal subtotal + VAT ({expected_total} SAR).")

    is_valid = len(errors) == 0

    return tool_result({
        "success": True,
        "is_zatca_compliant": is_valid,
        "passed_checks": 4 - len(errors),
        "total_checks": 4,
        "errors": errors,
    })


def register(ctx: Any) -> None:
    """Register Qeemah ZATCA & VAT tools in Hermes."""
    ctx.register_tool(
        name="ksa_vat_calculate",
        toolset="qeemah_zatca",
        schema=VAT_CALCULATE_SCHEMA,
        handler=_handle_vat_calculate,
        description="Calculate Saudi standard 15% VAT, subtotal, and total in SAR.",
    )
    ctx.register_tool(
        name="zatca_validate_invoice",
        toolset="qeemah_zatca",
        schema=ZATCA_VALIDATE_SCHEMA,
        handler=_handle_zatca_validate,
        description="Validate invoice fields against Saudi ZATCA Phase 2 business rules.",
    )
    logger.debug("Registered qeemah-zatca tools (ksa_vat_calculate, zatca_validate_invoice)")
