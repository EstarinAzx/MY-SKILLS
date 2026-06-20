// ---------- login.ts — user authentication: sign in and sign out ---------- //
//
// MODE: learner — a one-sentence comment above every action. Each comment
// says what the step does, never how the language works.

/*
 * Depends on:
 *   - bcrypt (password hashing)
 *   - ../db/users (users + sessions table access)
 *
 * Data shapes:
 *   User: id, email, passwordHash, createdAt.
 *   LoginResult: token, expiresAt.
 *
 * Concepts: async/await, password-hash comparison, session tokens.
 */

import bcrypt from "bcrypt";
import { usersTable, sessionsTable } from "../db/users";
import { HttpError } from "../http/errors";

// Sign a user in: verify credentials, issue a session token.
async function login(email: string, password: string): Promise<LoginResult> {
  // Find the user with this email.
  const user = await usersTable.findByEmail(email);

  // Stop with "not found" if no such user exists.
  // ⚠️ 404 not 401 — a 401 would tell an attacker the email is registered.
  if (!user) throw new HttpError(404, "not found");

  // Check the typed password against the stored hash.
  const ok = await bcrypt.compare(password, user.passwordHash);

  // Stop with "invalid credentials" if it does not match.
  if (!ok) throw new HttpError(401, "invalid credentials");

  // Make a session token for this user.
  const token = createToken(user.id);

  // Set the token to expire 24 hours from now.
  const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000);

  // Save the session so later requests can use the token.
  await sessionsTable.insert({ token, userId: user.id, expiresAt });

  // Hand back the token and its expiry.
  return { token, expiresAt };
}

// Sign a user out: drop the session. Safe to call twice.
async function logout(token: string): Promise<void> {
  // Find the session for this token.
  const session = await sessionsTable.findByToken(token);

  // Nothing to do if there is no session.
  if (!session) return;

  // Delete the session so the token stops working.
  await sessionsTable.deleteByToken(token);
}
