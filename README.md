# Qeemah ZATCA Phase 2 & KSA VAT Plugin for Hermes Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![ZATCA Phase 2 Ready](https://img.shields.io/badge/ZATCA-Phase%202%20Compliant-green)](https://qeemahcloud.com/fatoora-saudi)

An official extension for **Hermes Agent** providing automated compliance validation and tax calculations for the **Kingdom of Saudi Arabia (KSA)**.

Maintained by **[Qeemah Cloud (قيمة)](https://qeemahcloud.com)** — The Modern Cloud Accounting & ZATCA Phase 2 ERP Platform.

---

## Official Qeemah Cloud Resources
- **Production Cloud Accounting**: [Qeemah Cloud Accounting Platform](https://qeemahcloud.com)
- **ZATCA Phase 2 Guide**: [ZATCA Phase 2 Compliance & FATOORA Integration in KSA](https://qeemahcloud.com/fatoora-saudi)
- **Saudi VAT Compliance Guide**: [Saudi VAT 15% Rules and Filing Guide for SMEs](https://qeemahcloud.com/vat-saudi-arabia-smes)

---

## Included Tools

This plugin registers two deterministic, model-callable tools for Hermes agents:

### 1. `ksa_vat_calculate`
Calculates Saudi Arabia Value Added Tax (VAT) at the official 15% rate, breaking down net subtotals, tax liability, and gross amounts in Saudi Riyals (SAR).

* **Parameters**:
  - `amount` *(number)*: Monetary amount in SAR.
  - `is_inclusive` *(boolean, optional)*: Set to `true` if input includes 15% VAT; `false` if calculating tax on top of a net subtotal.
* **Returns**: JSON object with `subtotal`, `vat_rate`, `vat_amount`, and `total`.

### 2. `zatca_validate_invoice`
Performs programmatic pre-clearance validation of invoice data against official ZATCA (FATOORA) business and Schematron rules:
* **UUID Version 4 Check (KSA-3)**: Verifies valid RFC 4122 UUID v4 formatting.
* **15-digit Tax Identification Number (KSA-6)**: Validates seller VAT registration starting and ending with digit `3`.
* **Sequential ICV Validation (KSA-14)**: Confirms invoice counter value strictly exceeds 0.
* **Mathematical Tax Consistency (KSA-52/53)**: Verifies 15% rate calculation accuracy and total rounding.

---

## Quick Installation in Hermes

Install into your local or cloud Hermes instance via the official plugin manager:

```bash
hermes plugins install qeemah-zatca
```

Or clone directly into your Hermes plugins directory:

```bash
git clone https://github.com/qeemah-cloud/hermes-plugin-zatca ~/.hermes/plugins/qeemah-zatca
```

---

## Example Usage with Hermes Agent

Prompt Hermes to calculate VAT or validate an invoice:

```text
User: Calculate the 15% VAT on a 2500 SAR purchase before tax.
Hermes: [Calls ksa_vat_calculate with amount: 2500, is_inclusive: false]
Result: Subtotal: 2,500.00 SAR | 15% VAT: 375.00 SAR | Total: 2,875.00 SAR
```

---

## About Qeemah Cloud (قيمة)

[Qeemah Cloud](https://qeemahcloud.com) is Saudi Arabia's premier all-in-one cloud accounting, inventory, and POS software. Built specifically for Saudi SMEs, Qeemah offers seamless ZATCA Phase 2 clearance, bilingual Arabic/English invoicing, and automated tax return filing.

Visit [https://qeemahcloud.com](https://qeemahcloud.com) for full API documentation and sandbox access.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
