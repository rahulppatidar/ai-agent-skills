# Leak response

Read when a plausible credential is staged, committed, or pushed. Keep credential values out of messages, commands, reports, and tickets.

## Establish where it went

Determine whether the value exists only in current files/the index, in local commits, or in remote history or shared artifacts. Check metadata without printing the value. If remote access or complete history is unavailable, state that exposure is uncertain; do not infer “never pushed” from the current branch's status alone.

- **Only staged/local file:** replace the value using the project's configuration mechanism. Rescan the index. Do not silently restage an entire partially staged file or discard unrelated work. Rotation may still be warranted if the value appeared in logs, chat, or another shared surface.
- **Committed locally:** stop propagation, explain the exposure, and correct the pending commits within the user's authorization. A later deletion commit leaves the value in history.
- **Pushed/shared or uncertain shared exposure:** advise prompt revocation/rotation at the provider and checking access logs. Rewriting Git history cannot invalidate a credential or recall other people's clones.

## Remediate within the request

1. Prioritize revocation/rotation of an exposed credential. Account for service dependencies and an authorized replacement rollout; do not unexpectedly revoke production access just because the user requested a repository scan. Give the owner concrete provider-specific next steps when you cannot act.
2. Replace hardcoded values with the existing runtime configuration or secret-store mechanism. Use clearly synthetic examples. Never put the replacement credential in the repository or conversation.
3. If a local-only file should remain on disk, add a narrow ignore rule and stop tracking only the confirmed file when authorized. Explain that `.gitignore` does not remove existing index entries or history. Avoid broad file-extension bans: public certificates and other legitimate artifacts may use the same extensions.
4. If history cleanup is needed, prepare the exact refs/paths, recovery copy, impact on tags/signatures/branches, collaborator instructions, and a verification plan. Require specific authorization for shared-history rewrites and force pushes; a request to scan or install a hook does not grant it. Keep recovery copies private because they retain the secret. Do not silently delete files, reset work, expire reflogs, or run garbage collection.
5. Rescan the corrected scope and relevant history; report unresolved provider actions, remote caches/forks/clones, or missing coverage. Add prevention if requested.

Handle a false positive with evidence and the narrowest supported exception, recording a reason. Do not paste a real value into a web regex tester or a baseline rationale. If a credential cannot be checked online, retain its suspected status rather than dismissing it.

Completion means the authorized local changes are verified and any remaining rotation, external cleanup, or coordination is clearly assigned. Never imply that a credential is revoked merely because Git no longer contains it.
