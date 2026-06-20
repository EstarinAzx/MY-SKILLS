# scripts

Personal helper scripts for the `~/.claude` setup. Each is exposed as a global
command through a thin function in the PowerShell profile.

## How a script becomes a global command

A script in this folder is **not** on `PATH`. It is made global by a one-line
wrapper function in the PowerShell profile, which runs at the start of every
PowerShell session:

```
D:\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
```

Pattern for any new script:

```powershell
function <name> { & 'C:\Users\S.D\.claude\scripts\<name>.ps1' @args }
```

- The profile auto-runs on every session start, so the function exists in every
  shell and every directory — that is what makes it feel "global".
- `@args` splats whatever you typed after the command straight into the script,
  so flags like `-Force` pass through.
- To add a new command: drop a `.ps1` here, add one wrapper line to the profile,
  open a new shell (or `. $PROFILE` to reload).

> Note: a script run by an external tool / non-interactive shell won't see these
> functions, because the interactive profile isn't loaded there. They only exist
> in your normal terminal sessions.

---

## getclaude

Drops the canonical `CLAUDE.md` template into the current directory.

**Files**
- Script: `C:\Users\S.D\.claude\scripts\getclaude.ps1`
- Template source: `C:\Users\S.D\.claude\template\IN USE\CLAUDE.md`
- Profile wrapper: `function getclaude { & 'C:\Users\S.D\.claude\scripts\getclaude.ps1' @args }`

**Usage**

```powershell
getclaude          # copy template CLAUDE.md into the current dir
getclaude -Force   # overwrite an existing CLAUDE.md here
```

**Behavior**
1. Source = `...\template\IN USE\CLAUDE.md` (hardcoded canonical copy).
2. Destination = `CLAUDE.md` in the current working directory.
3. Aborts with an error if the template is missing.
4. Aborts with a warning if a `CLAUDE.md` already exists here and `-Force` was
   not passed — so a project-specific `CLAUDE.md` is never clobbered silently.
5. Otherwise copies source → destination and prints `CLAUDE.md -> <path>`.

A copy of `getclaude.ps1` also lives in `template\IN USE\` so the script travels
with the template it depends on.
