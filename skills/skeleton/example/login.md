---
code_file: src/auth/login.ts
last_synced: 2026-05-16
status: synced
---

## Depends on

- express (web framework — provides Request / Response types)
- bcrypt (password hashing and comparison)
- jsonwebtoken (signs and verifies JWTs)
- [users db module](../db/users.md)
- [sessions db module](../db/sessions.md)
- [config](../config.md) — reads JWT_SECRET and SESSION_TTL_HOURS

## Data shapes

User has: id (number), email (string), passwordHash (string), createdAt (date).

LoginRequest has: email (string) and password (string).

LoginResult has: token (string) and expiresAt (date).

## function login(req, res)

1. Read email and password from the request body. Treat the body as a LoginRequest.
2. First check: if either email or password is missing or empty, send back 400 "missing credentials" and stop.
3. Ask the users db to find a user by email.
4. If no user is found, send back 401 "invalid credentials". Note: use the same 401 message as a wrong password, so an attacker can't tell which one was wrong.
5. Otherwise, compare the supplied password to the stored passwordHash using bcrypt. Wait for the comparison to finish before continuing.
6. If the comparison fails, send back 401 "invalid credentials".
7. Otherwise, create a new JWT signed with JWT_SECRET. The payload contains the user id and an "iat" (issued-at) timestamp.
8. Compute expiresAt as now plus SESSION_TTL_HOURS hours.
9. Ask the sessions db to store a new row with the token, user id, and expiresAt.
10. Send back 200 with a LoginResult containing the token and expiresAt.

## function logout(req, res)

1. Read the Authorization header from the request.
2. First check: if the header is missing or does not start with "Bearer ", send back 204 (logout is idempotent — no token means already logged out).
3. Otherwise, extract the token (everything after "Bearer ").
4. Ask the sessions db to delete the session row matching that token.
5. Whether or not a row existed, send back 204.

## function refresh(req, res)

1. Read the token from the Authorization header (same "Bearer ..." pattern as logout).
2. If the header is missing or malformed, send back 401 "missing token".
3. Attempt to verify the token using JWT_SECRET.
4. If verification fails (bad signature or expired), send back 401 "invalid token".
5. Otherwise, look up the matching session in the sessions db.
6. If no session is found, send back 401 "session revoked".
7. Otherwise, create a new JWT for the same user id with a fresh "iat" timestamp.
8. Compute a new expiresAt as now plus SESSION_TTL_HOURS hours.
9. Ask the sessions db to replace the old row: delete the old token row, insert the new one.
10. Send back 200 with a LoginResult containing the new token and expiresAt.

## This runs LATER when a session expires

The sessions db has a background sweeper (described in [sessions db](../db/sessions.md)) that deletes rows where expiresAt is in the past. This file does not run that sweeper — it only writes the rows. The cleanup is the sweeper's job.
