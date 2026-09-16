"""
Demo Mode content (spec section 27).

A judge should be able to click "Try Demo" and immediately see summary,
risks, clauses, timeline, chat, and lawyer questions -- without uploading
a file or needing an LLM_API_KEY configured. This module supplies a
realistic sample Employment Agreement plus a fully pre-baked analysis so
the whole UI is explorable offline. If an LLM_API_KEY IS configured, the
demo document's chat still runs through the real RAG pipeline against
this same text, so judges can also ask free-form questions live.
"""

DEMO_DOCUMENT_TEXT = """EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into between Nimbus Retail Pvt Ltd \
("Company") and the undersigned employee ("Employee").

1. Position and Duties
The Employee shall serve as Senior Software Engineer and shall perform duties as \
reasonably assigned by the Company. The Employee agrees to devote full working time and \
best efforts to the Company's business.

2. Compensation
The Company shall pay the Employee a gross monthly salary of INR 1,20,000, payable on the \
last working day of each month. The Employee shall also be eligible for an annual \
discretionary bonus of up to 15% of base salary, at the Company's sole discretion.

3. Term and Termination
This Agreement shall continue until terminated by either party. The Company may terminate \
this Agreement at any time, with or without cause, upon 15 days written notice. The \
Employee must provide the Company with 90 days written notice prior to resignation. \
Failure to serve the full notice period will result in a penalty equal to two months' \
gross salary, deductible from any final settlement.

4. Confidentiality
The Employee agrees to keep confidential all proprietary information of the Company \
during employment and for a period of 5 years after termination, without geographic \
limitation.

5. Intellectual Property
All work product, inventions, code, designs, and other intellectual property created by \
the Employee during the course of employment, whether or not during working hours or \
using Company resources, shall be the sole and exclusive property of the Company.

6. Non-Compete
For a period of 12 months following termination of employment, the Employee shall not \
directly or indirectly engage in any business that competes with the Company, anywhere \
in India.

7. Indemnification
The Employee shall indemnify and hold harmless the Company from any and all losses, \
damages, and legal costs arising from the Employee's actions, without any cap or limit \
on the amount of such indemnification.

8. Dispute Resolution
Any dispute arising out of this Agreement shall be resolved through binding arbitration \
in Mumbai, India, in accordance with the Arbitration and Conciliation Act, and the \
Employee waives the right to pursue claims in civil court.

9. Governing Law
This Agreement shall be governed by the laws of India, and the courts of Mumbai shall \
have exclusive jurisdiction.

10. Renewal
This Agreement shall automatically renew for successive one-year terms unless either \
party provides written notice of non-renewal at least 60 days before the renewal date.
"""

DEMO_DOCUMENT_TYPE = "Employment Agreement"

DEMO_ANALYSIS = {
    "document_type": DEMO_DOCUMENT_TYPE,
    "parties": ["Nimbus Retail Pvt Ltd (Company)", "Employee (Senior Software Engineer)"],
    "executive_summary": (
        "This is an employment agreement for a Senior Software Engineer role paying "
        "INR 1,20,000 per month plus a discretionary bonus. It contains several "
        "one-sided terms worth reviewing: the company can end employment with only "
        "15 days' notice while the employee must give 90 days, there's an uncapped "
        "indemnification clause, and a 12-month non-compete. All intellectual property "
        "created during employment belongs to the company, even outside working hours."
    ),
    "key_points": [
        "Monthly salary of INR 1,20,000 with an up-to-15% discretionary annual bonus",
        "Company can terminate with 15 days' notice; employee must give 90 days",
        "Missing the notice period costs the employee two months' salary",
        "All IP created during employment belongs to the company, even off-hours work",
        "12-month non-compete applying anywhere in India",
        "Disputes go to binding arbitration in Mumbai, not civil court",
    ],
    "your_obligations": [
        "Devote full working time and best efforts to the company",
        "Give 90 days' written notice before resigning",
        "Keep company information confidential for 5 years after leaving",
        "Not compete with the company for 12 months after leaving, anywhere in India",
        "Indemnify the company for losses/legal costs from your actions, with no stated cap",
    ],
    "other_party_obligations": [
        "Pay INR 1,20,000 gross monthly salary on the last working day of each month",
        "Consider the employee for an annual discretionary bonus of up to 15%",
        "Give 15 days' written notice before terminating the employee",
    ],
    "important_dates": [
        {"label": "Monthly pay date", "detail": "Last working day of each month"},
        {"label": "Employee resignation notice", "detail": "90 days before leaving"},
        {"label": "Company termination notice", "detail": "15 days"},
        {"label": "Non-compete period", "detail": "12 months after termination"},
        {"label": "Confidentiality period", "detail": "5 years after termination"},
        {"label": "Renewal notice deadline", "detail": "60 days before each renewal date"},
    ],
    "financial_terms": [
        {"label": "Gross monthly salary", "amount": "INR 1,20,000"},
        {"label": "Annual discretionary bonus", "amount": "Up to 15% of base salary"},
        {"label": "Early-resignation penalty", "amount": "Two months' gross salary"},
    ],
    "governing_law": "India; exclusive jurisdiction of the courts of Mumbai (subject to the arbitration clause)",
    "attention_score": 72,
}

DEMO_CLAUSES = [
    {
        "clause_type": "Termination",
        "original_text": "The Company may terminate this Agreement at any time, with or without cause, upon 15 days written notice.",
        "plain_explanation": "Simply put: the company can end your employment for almost any reason, or no stated reason, as long as it gives you 15 days' notice.",
        "why_it_matters": "This gives the company broad flexibility to end the relationship quickly, while you're required to give six times as much notice (90 days) if you want to leave.",
        "what_to_check": ["Is 15 days enough time for you to find new work?", "Does 'without cause' align with your expectations for job security?"],
        "section_label": "Term and Termination",
    },
    {
        "clause_type": "Intellectual Property",
        "original_text": "All work product, inventions, code, designs...created by the Employee during the course of employment...whether or not during working hours...shall be the sole and exclusive property of the Company.",
        "plain_explanation": "Simply put: anything you create while employed here -- even a side project on a weekend using your own laptop -- may legally belong to the company, not you.",
        "why_it_matters": "This is broader than many standard IP clauses, which usually limit company ownership to work done using company resources or related to company business.",
        "what_to_check": ["Does this cover personal projects unrelated to your job?", "Can this be narrowed to work related to company business or using company resources?"],
        "section_label": "Intellectual Property",
    },
    {
        "clause_type": "Non-Compete",
        "original_text": "For a period of 12 months following termination of employment, the Employee shall not directly or indirectly engage in any business that competes with the Company, anywhere in India.",
        "plain_explanation": "Simply put: for a full year after leaving, you may be restricted from working for or starting a competing business anywhere in the country.",
        "why_it_matters": "A nationwide, 12-month restriction can meaningfully limit your next job search, especially in a specialized field.",
        "what_to_check": ["Is this scope (12 months, all of India) enforceable where you live?", "Could this be narrowed by role, region, or duration?"],
        "section_label": "Non-Compete",
    },
    {
        "clause_type": "Indemnification",
        "original_text": "The Employee shall indemnify and hold harmless the Company from any and all losses, damages, and legal costs arising from the Employee's actions, without any cap or limit on the amount of such indemnification.",
        "plain_explanation": "Simply put: if your actions cause the company a loss, you could be personally on the hook to cover it, with no maximum amount specified.",
        "why_it_matters": "An uncapped indemnification clause is unusual for a standard employee (as opposed to a contractor or executive) and could expose you to significant personal financial risk.",
        "what_to_check": ["Is there a reasonable cap that could be negotiated?", "Does the company carry insurance that would apply first?"],
        "section_label": "Indemnification",
    },
    {
        "clause_type": "Arbitration",
        "original_text": "Any dispute...shall be resolved through binding arbitration in Mumbai...and the Employee waives the right to pursue claims in civil court.",
        "plain_explanation": "Simply put: if there's ever a dispute, you'd go through a private arbitration process instead of suing in court, and you're giving up the right to sue.",
        "why_it_matters": "Arbitration can be faster and more private, but it also typically limits appeal rights and may favor whichever party is more experienced with the process.",
        "what_to_check": ["Who bears the cost of arbitration proceedings?", "Is Mumbai a practical location for you if a dispute arises?"],
        "section_label": "Dispute Resolution",
    },
]

DEMO_RISK_FINDINGS = [
    {
        "clause_snippet": "Employee must provide 90 days written notice...Company...15 days written notice.",
        "risk_level": "high",
        "category": "One-sided termination",
        "explanation": "The notice period is highly asymmetric (90 days vs. 15 days), which may deserve careful review because it limits your flexibility much more than the company's.",
        "why_it_matters": "If you need to leave quickly for a new opportunity or personal reasons, the 90-day requirement (backed by a financial penalty) could be a real constraint.",
        "suggested_question": "Is the 90-day resignation notice negotiable, and is the two-month penalty enforceable in my jurisdiction?",
        "section_label": "Term and Termination",
    },
    {
        "clause_snippet": "shall indemnify and hold harmless the Company...without any cap or limit",
        "risk_level": "high",
        "category": "Uncapped indemnification",
        "explanation": "An indemnification clause with no stated cap may deserve careful review because your personal financial exposure is theoretically unlimited.",
        "why_it_matters": "Most employee-side indemnification clauses (if present at all) are capped or limited to gross negligence/willful misconduct.",
        "suggested_question": "Can we add a cap to the indemnification obligation, or limit it to gross negligence or willful misconduct?",
        "section_label": "Indemnification",
    },
    {
        "clause_snippet": "created by the Employee during the course of employment, whether or not during working hours or using Company resources",
        "risk_level": "high",
        "category": "Broad IP assignment",
        "explanation": "IP assignment extending to off-hours, personal-resource work may deserve careful review because it's broader than typical employment IP clauses.",
        "why_it_matters": "This could affect your ability to own side projects, open-source contributions, or personal inventions made outside work.",
        "suggested_question": "Can the IP clause be limited to work related to the company's business or created using company resources?",
        "section_label": "Intellectual Property",
    },
    {
        "clause_snippet": "shall not...engage in any business that competes with the Company, anywhere in India",
        "risk_level": "medium",
        "category": "Broad non-compete",
        "explanation": "A 12-month, nationwide non-compete may deserve careful review because of its geographic and duration scope.",
        "why_it_matters": "Enforceability of non-competes varies significantly by jurisdiction in India, so this may or may not be enforceable as written.",
        "suggested_question": "Is this non-compete clause enforceable in my state, and could its scope be narrowed?",
        "section_label": "Non-Compete",
    },
    {
        "clause_snippet": "automatically renew for successive one-year terms unless either party provides written notice of non-renewal at least 60 days",
        "risk_level": "medium",
        "category": "Automatic renewal",
        "explanation": "Automatic renewal clauses may deserve a calendar reminder because missing the 60-day window locks in another full year.",
        "why_it_matters": "If your circumstances change, forgetting this deadline could commit you to terms you no longer want.",
        "suggested_question": "Is there flexibility to convert this to an evergreen term without a hard renewal deadline?",
        "section_label": "Renewal",
    },
    {
        "clause_snippet": "waives the right to pursue claims in civil court",
        "risk_level": "medium",
        "category": "Arbitration / waived court access",
        "explanation": "Waiving civil court access may deserve careful review since arbitration outcomes are harder to appeal.",
        "why_it_matters": "This affects your options if a serious dispute arises later.",
        "suggested_question": "What are the practical differences in cost and process between arbitration and civil court for a dispute like this?",
        "section_label": "Dispute Resolution",
    },
    {
        "clause_snippet": "Employee agrees to keep confidential all proprietary information...for a period of 5 years after termination",
        "risk_level": "low",
        "category": "Confidentiality duration",
        "explanation": "A 5-year post-employment confidentiality period is on the longer side but is a fairly standard, low-concern term for this document type.",
        "why_it_matters": "Generally reasonable, but worth noting the duration if you plan to work in a closely related field.",
        "suggested_question": "Is 5 years standard for this industry, or could it be shortened?",
        "section_label": "Confidentiality",
    },
    {
        "clause_snippet": "gross monthly salary of INR 1,20,000, payable on the last working day of each month",
        "risk_level": "standard",
        "category": "Standard payment term",
        "explanation": "This is a standard, clearly stated compensation term with low concern.",
        "why_it_matters": "Clear payment terms are good practice and don't typically require legal review.",
        "suggested_question": None,
        "section_label": "Compensation",
    },
]

DEMO_CHECKLIST = [
    {"text": "Confirm whether the 90-day resignation notice is negotiable", "explanation": "This is the most asymmetric term in the agreement."},
    {"text": "Ask about capping the indemnification clause", "explanation": "An uncapped clause creates open-ended personal financial risk."},
    {"text": "Clarify the scope of the IP assignment clause", "explanation": "As written it may cover personal, off-hours projects."},
    {"text": "Check non-compete enforceability in your state", "explanation": "Enforceability varies significantly by jurisdiction."},
    {"text": "Set a calendar reminder 75 days before the renewal date", "explanation": "Missing the 60-day non-renewal window auto-renews for another year."},
    {"text": "Understand the arbitration process before signing", "explanation": "You are waiving the right to pursue claims in civil court."},
]

DEMO_LAWYER_PREP = {
    "summary_for_lawyer": (
        "This is a standard-looking Employment Agreement for a Senior Software Engineer "
        "role in India, but it contains several employee-unfavorable terms: an asymmetric "
        "notice period (90 days employee / 15 days company) with a two-month salary penalty, "
        "an uncapped indemnification obligation, a broad IP assignment extending to off-hours "
        "work, and a 12-month nationwide non-compete. The employee would like guidance on "
        "which of these terms are negotiable or potentially unenforceable."
    ),
    "questions": [
        "Is the 90-day resignation notice period and its associated two-month salary penalty enforceable?",
        "Can the indemnification clause be capped or limited to gross negligence/willful misconduct?",
        "Is the IP assignment clause overly broad, and can it be limited to work related to company business?",
        "Is a 12-month, nationwide non-compete enforceable in my state?",
        "What are the practical implications of waiving civil court access in favor of arbitration?",
        "Are there any other clauses in this agreement that are unusual compared to industry-standard employment contracts?",
    ],
    "documents_to_bring": [
        "This employment agreement (signed and unsigned versions if both exist)",
        "Your offer letter, if separate from this agreement",
        "Any prior employment agreements for comparison",
        "Notes on any verbal promises made during negotiation that aren't reflected in this document",
    ],
}
