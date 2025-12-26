# Security Documentation

## Authentication & Authorization Strategy

### Overview

The News application implements a JWT-based authentication system with refresh token rotation for enhanced security. This approach provides:

- Stateless authentication for API scalability
- Short-lived access tokens to limit exposure
- Refresh token rotation to prevent token replay attacks
- Server-side token invalidation on logout

### Token Strategy

#### Access Tokens

- **Lifetime**: 15 minutes
- **Storage**: Can be stored in localStorage or httpOnly cookies
- **Purpose**: Authenticate API requests
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Payload**: userId, email, iat, exp

#### Refresh Tokens

- **Lifetime**: 7 days
- **Storage**: httpOnly cookies with secure and SameSite flags
- **Purpose**: Obtain new access tokens without re-authentication
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Server-side tracking**: Token hash stored in database for invalidation

### Token Rotation Flow

1. User logs in → Server generates access token + refresh token
2. Server stores hash of refresh token in database
3. Client includes access token in API requests
4. When access token expires → Client uses refresh token to get new tokens
5. Server validates refresh token, revokes old one, issues new tokens
6. Server stores hash of new refresh token

### Password Security

#### Hashing Algorithm: Argon2id

We use Argon2id, the winner of the Password Hashing Competition and recommended by OWASP:

- **Type**: Argon2id (hybrid of Argon2i and Argon2d)
- **Memory cost**: 64 MB (65536 KiB)
- **Time cost**: 3 iterations
- **Parallelism**: 4 threads
- **Salt**: Automatically generated per password

#### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- No password reuse (not implemented yet, but database schema supports)

### Rate Limiting

#### General API Endpoints

- **Window**: 15 minutes
- **Max requests**: 100 requests per window
- **Applies to**: All API endpoints except auth endpoints

#### Authentication Endpoints

- **Window**: 15 minutes
- **Max requests**: 5 requests per window
- **Applies to**: /auth/signup, /auth/login
- **Skip on success**: Failed attempts count, successful ones don't

### CORS Configuration

#### Development

- **Origin**: http://localhost:3001
- **Credentials**: Enabled
- **Methods**: GET, POST, PUT, PATCH, DELETE, OPTIONS
- **Headers**: Content-Type, Authorization

#### Production

- **Origin**: Specific production domain (configured via environment variable)
- **No wildcards**: Explicit origin allowlist only

### Security Headers (Helmet.js)

The application uses Helmet.js to set secure HTTP headers:

#### Content Security Policy (CSP)

```
default-src 'self'
style-src 'self' 'unsafe-inline'
script-src 'self'
img-src 'self' data: https:
```

#### Strict Transport Security (HSTS)

```
max-age: 31536000 (1 year)
includeSubDomains: true
preload: true
```

#### Other Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block

### Cookie Security

All cookies set by the application include:

- **httpOnly**: true (prevents JavaScript access)
- **secure**: true (HTTPS only in production)
- **sameSite**: 'strict' (prevents CSRF)
- **domain**: Not set (defaults to current domain)
- **path**: / (all paths)

### Input Validation

#### Validation Strategy

We use express-validator for comprehensive input validation:

1. **Type validation**: Ensure correct data types
2. **Format validation**: Email, URL, etc.
3. **Length validation**: Min/max string lengths
4. **Range validation**: Number ranges
5. **Custom validation**: Business logic rules
6. **Sanitization**: Normalize and clean input

#### Example: User Signup

```typescript
{
  email: 'email + normalizeEmail',
  password: 'min 8 chars + complexity rules',
  display_name: 'optional + max 100 chars + trimmed'
}
```

#### Rejected Fields

Unknown fields in request bodies are rejected to prevent:

- Parameter pollution
- Mass assignment vulnerabilities
- Injection attacks

### Logging & Monitoring

#### PII Redaction

The logger automatically redacts sensitive fields:

- password
- email
- token
- authorization
- cookie

#### Log Levels

- **error**: Errors and exceptions
- **warn**: Warnings and unusual conditions
- **info**: General information (default)
- **debug**: Detailed debugging (development only)

#### What We Log

✅ **Do log**:

- Request method and path
- Response status codes
- Error messages (sanitized)
- Timestamp and duration
- User actions (without PII)

❌ **Don't log**:

- Passwords (plain or hashed)
- Tokens (access or refresh)
- Full email addresses in production
- Request bodies on auth endpoints
- Authorization headers

### Attack Prevention

#### SQL Injection

- **Protection**: Parameterized queries via pg library
- **Never**: String concatenation for SQL

#### Cross-Site Scripting (XSS)

- **Protection**: React auto-escapes output
- **Additional**: CSP headers
- **Validation**: Input sanitization

#### Cross-Site Request Forgery (CSRF)

- **Protection**: SameSite cookies
- **Additional**: Consider CSRF tokens for state-changing operations
- **Note**: SameSite=Strict provides strong protection

#### User Enumeration

- **Protection**: Consistent error messages
- **Login/Signup**: Same error for non-existent users and wrong passwords
- **Timing**: Constant-time password verification

#### Brute Force

- **Protection**: Rate limiting on auth endpoints
- **Lockout**: Consider account lockout after N failed attempts
- **Monitoring**: Log failed authentication attempts

#### Token Theft/Replay

- **Protection**: Short-lived access tokens
- **Additional**: Refresh token rotation
- **Server-side**: Token invalidation on logout

#### Horizontal Privilege Escalation

- **Protection**: Always check user_id in queries
- **Example**: `WHERE user_id = $1 AND id = $2`
- **Never**: Trust client-provided user IDs

### Database Security

#### Connection Security

- **SSL/TLS**: Required in production
- **Credentials**: Environment variables only
- **Principle of least privilege**: App user has minimal permissions

#### Data Protection

- **Encryption at rest**: Database-level encryption
- **Encryption in transit**: SSL/TLS connections
- **Backups**: Encrypted and access-controlled

#### Schema Security

- **Foreign keys**: Enforce referential integrity
- **Constraints**: Enforce data rules at DB level
- **Indexes**: Sensitive to timing attacks (be careful)

### Environment Variables

#### Required for Production

```env
NODE_ENV=production
JWT_ACCESS_SECRET=<strong-random-secret-64-chars>
JWT_REFRESH_SECRET=<different-strong-random-secret-64-chars>
COOKIE_SECRET=<strong-random-secret-32-chars>
CORS_ORIGIN=https://your-production-domain.com
DB_PASSWORD=<strong-database-password>
```

#### Secret Generation

Use cryptographically secure random generation:

```bash
# Generate secure secrets
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### Security Checklist for Production

- [ ] Change all default secrets in .env
- [ ] Enable HTTPS (TLS 1.2+)
- [ ] Set NODE_ENV=production
- [ ] Configure proper CORS origin
- [ ] Enable database SSL
- [ ] Set up log monitoring and alerts
- [ ] Configure firewall rules
- [ ] Implement rate limiting at load balancer
- [ ] Set up security scanning (CodeQL, Snyk, etc.)
- [ ] Enable WAF (Web Application Firewall)
- [ ] Configure DDoS protection
- [ ] Set up intrusion detection
- [ ] Regular security audits
- [ ] Dependency vulnerability scanning
- [ ] Penetration testing

### Compliance Considerations

#### GDPR

- User data collection minimization
- Right to access (export user data)
- Right to deletion (delete user account)
- Right to rectification (update user data)
- Privacy policy disclosure

#### Data Retention

- Refresh tokens: Auto-delete expired tokens
- User accounts: Soft delete with retention period
- Logs: Rotate and archive with retention policy

### Incident Response

#### Security Breach Response Plan

1. **Detect**: Monitor for anomalies
2. **Assess**: Determine scope and impact
3. **Contain**: Stop the breach
4. **Eradicate**: Remove threat
5. **Recover**: Restore normal operations
6. **Review**: Post-incident analysis

#### Token Compromise

If tokens are compromised:

1. Revoke all refresh tokens for affected users
2. Force re-authentication
3. Rotate JWT secrets (requires all users to re-login)
4. Investigate how tokens were compromised
5. Implement additional protections

### Regular Security Maintenance

#### Weekly

- Review error logs for anomalies
- Check failed authentication attempts

#### Monthly

- Update dependencies (security patches)
- Review access logs for suspicious patterns
- Test backup restoration

#### Quarterly

- Security audit of new features
- Penetration testing
- Review and update security policies
- Dependency vulnerability scan

#### Annually

- Comprehensive security audit
- Third-party security assessment
- Disaster recovery drill
- Update compliance documentation

## Contact

For security issues, please email: security@example.com (Do NOT open public issues for security vulnerabilities)
