# PaiseWise AI Features - DPDP Compliance Document

## 1. Purpose

This document describes the data handling, privacy controls, retention,
and user rights implemented for AI features in the PaiseWise application.

This document is intended for internal compliance review and legal advisor
approval before production launch.

---

## 2. AI Features Covered

The following AI features are covered:

- Financial jargon explanation
- Financial education / RAG question answering
- Portfolio diversification analysis
- Market context and news analysis
- AI quality monitoring
- LLM cost monitoring
- A/B experimentation
- AI response feedback

---

## 3. Data Collected

The AI service may process the following categories of data:

### User/Application Data

- User ID
- User-provided questions or prompts
- Feature name
- Language preference
- AI response metadata
- User feedback
- Experiment assignment information

### AI Monitoring Data

- Quality score
- Response success/failure
- Response time
- Experiment ID
- Variant ID
- LLM token usage
- LLM cost information
- Timestamps

The AI service is designed to avoid sending unnecessary personal
information to external LLM providers.

---

## 4. Personal Data Protection

A PII scrubbing layer is implemented before prompts are sent to an
external LLM service.

The scrubber detects and replaces common personal identifiers including:

- Email addresses
- Indian phone numbers
- PAN numbers
- Aadhaar numbers

Detected values are replaced with redacted placeholders before the
LLM request is made.

Example:

Original:

    Contact me at example@email.com

Processed:

    Contact me at [REDACTED_EMAIL]

Generic names are not automatically removed because reliable name detection
requires additional contextual information. The application should avoid
sending unnecessary names to the LLM.

---

## 5. Purpose of Data Processing

Data is processed only for application and AI-service purposes, including:

- Providing financial education responses
- Explaining financial terminology
- Generating portfolio diversification analysis
- Providing market/news context
- Monitoring AI response quality
- Monitoring LLM usage and cost
- Evaluating AI experiments
- Improving AI feature reliability
- Processing user feedback
- Maintaining application security and reliability

---

## 6. LLM Processing

Before an external LLM API call:

1. The application receives the AI request.
2. The prompt is prepared.
3. The PII scrubber processes the prompt.
4. Detected personal identifiers are replaced with redacted values.
5. The sanitized prompt is sent to the LLM provider.
6. The AI response is returned to the application.

This reduces unnecessary exposure of personal identifiers to external
LLM providers.

---

## 7. Data Retention

LLM cost and call records are subject to a 90-day retention mechanism.

Records older than 90 days are automatically removed when the relevant
storage is accessed.

The retention mechanism applies to:

- LLM cost records
- AI call-related stored records covered by the retention implementation

Retention periods should be reviewed and approved by the legal/compliance
team before production launch.

---

## 8. Right to Deletion

A centralized user-data deletion service has been implemented.

The deletion service removes AI-generated/user-associated records from:

- Experiment logs
- AI quality evaluation records
- User feedback records
- LLM cost records
- LLM cost backup records

The deletion service accepts a user ID and removes records associated
with that user.

### Deletion Test

A dedicated test user was created for validation:

    DELETE_TEST_USER

The test successfully deleted:

- 1 experiment record
- 1 quality evaluation
- 1 feedback record
- 1 cost record
- 1 backup cost record

Total records deleted:

    5

A post-deletion verification confirmed that no records for the test user
remained in the five tested stores.

---

## 9. Data Security Controls

Current controls include:

- PII scrubbing before external LLM calls
- User-specific data deletion
- 90-day retention mechanism for applicable LLM records
- AI service health monitoring
- Circuit breaker for LLM failures
- Application-level access controls
- Monitoring of AI service behavior

---

## 10. AI-Generated Content

AI-generated content is used to provide application functionality such as
financial education and analysis.

AI responses should not be treated as personalized financial advice unless
the application's approved product and legal requirements explicitly
permit such functionality.

---

## 11. User Rights

The application should support applicable user privacy rights, including:

- Right to access applicable personal data
- Right to correction of inaccurate data
- Right to deletion where applicable
- Right to withdraw consent where applicable
- Right to raise privacy-related grievances

The exact implementation and scope of these rights must be reviewed by
the legal/compliance team.

---

## 12. Third-Party AI Providers

The application may use external AI/LLM services for AI processing.

Before production launch, the organization should verify:

- Applicable provider data-processing terms
- Data retention settings
- Whether submitted prompts are used for provider model training
- Data residency requirements
- Security requirements
- Contractual/data-processing agreements
- Applicable cross-border data-transfer requirements

---

## 13. Data Minimization

The AI service should send only the information necessary to perform the
requested AI operation.

Personal information that is not required for an AI operation should not
be included in the prompt.

---

## 14. Compliance Review

This document describes the technical controls implemented by the AI
service. It is not a legal opinion.

Before production launch, the document and implementation must be reviewed
by the organization's legal/compliance advisor.

### Legal Advisor Sign-Off

Status: Pending

Reviewer:

Date:

Comments:

Approval:

---

## 15. Implementation Status

| Control                                | Status    |
| -------------------------------------- | --------- |
| Prompt PII audit                       | Completed |
| PII scrubber                           | Completed |
| PII scrubber integrated with LLM calls | Completed |
| 90-day retention                       | Completed |
| Right-to-deletion service              | Completed |
| Right-to-deletion testing              | Completed |
| DPDP compliance document               | Drafted   |
| Legal/compliance review                | Pending   |
| Production approval                    | Pending   |

## 16. Legal / Compliance Review Checklist

The legal or compliance reviewer should verify the following before
production launch:

- [ ] Data collected by AI features has been reviewed.
- [ ] Purpose of each data-processing activity has been reviewed.
- [ ] PII handling and redaction controls have been reviewed.
- [ ] LLM/third-party provider data-processing terms have been reviewed.
- [ ] Data retention periods have been approved.
- [ ] User deletion process has been reviewed.
- [ ] Applicable user privacy rights have been reviewed.
- [ ] Data security controls have been reviewed.
- [ ] Cross-border data-transfer requirements have been reviewed where applicable.
- [ ] Required notices/consent mechanisms have been reviewed.
- [ ] Production deployment has been approved.

### Reviewer Information

Reviewer Name:

Organization:

Review Date:

Decision:

Comments:

Signature / Approval:
