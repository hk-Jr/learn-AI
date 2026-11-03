# Enterprise Cloud Infrastructure & Data Security Policy

## Policy Statement: Access Control & Zero Trust
All corporate resources adhere strictly to the principle of Least Privilege and Zero Trust Architecture. Access to production cloud environments requires Multi-Factor Authentication (MFA) utilizing FIDO2 hardware security keys. Password-only authentication and SMS-based verification are strictly prohibited.

## Data Encryption Standards
- **Data at Rest**: All storage volumes, vector database clusters, and object storage buckets must use AES-256 GCM encryption.
- **Data in Transit**: All network communications require TLS 1.3 encryption with Perfect Forward Secrecy (PFS).
- **Key Management**: Customer-managed encryption keys (CMEK) must be rotated automatically every 90 days.

## Incident Response Protocol
Security incidents classified as Severity-1 require incident commander mobilization within 15 minutes of detection. All forensic logs must be preserved in immutable, write-once-read-many (WORM) storage for a minimum retention period of 365 days.