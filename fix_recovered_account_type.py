"""
Fix: recoveredAccount was an AccountExport (the save-file DTO), but
ServiceResult<Account> needs the real live Account domain object.
restoreAccount(export) already inserts it into accountService's live
store under export.id - just look it up via accountById() afterward.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "    val recoveredAccount = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }\n"
    "        ?: return ServiceResult.Failure(\"Recovered cloud data but couldn't match it to this email.\")\n"
    "\n"
    "    sessionManager.saveSession(recoveredAccount.id)\n"
    "    _currentAccountId.value = recoveredAccount.id\n"
    "    refreshCurrency()\n"
    "    _currentSupabaseCharacterId.value = supabaseCharacterId\n"
    "    _characterSyncError.value = null\n"
    "\n"
    "    val recoveredCharacter = recovered.characters.firstOrNull { it.accountId == recoveredAccount.id }\n"
    "    if (recoveredCharacter != null) {\n"
    "        _currentCharacterId.value = recoveredCharacter.id\n"
    "    }\n"
    "\n"
    "    return ServiceResult.Success(recoveredAccount)\n"
    "}\n"
)
new = (
    "    val recoveredAccountExport = recovered.accounts.firstOrNull { it.email.equals(email, ignoreCase = true) }\n"
    "        ?: return ServiceResult.Failure(\"Recovered cloud data but couldn't match it to this email.\")\n"
    "    val recoveredAccount = accountService.accountById(recoveredAccountExport.id)\n"
    "        ?: return ServiceResult.Failure(\"Recovered account data but couldn't load it.\")\n"
    "\n"
    "    sessionManager.saveSession(recoveredAccount.id)\n"
    "    _currentAccountId.value = recoveredAccount.id\n"
    "    refreshCurrency()\n"
    "    _currentSupabaseCharacterId.value = supabaseCharacterId\n"
    "    _characterSyncError.value = null\n"
    "\n"
    "    val recoveredCharacter = recovered.characters.firstOrNull { it.accountId == recoveredAccount.id }\n"
    "    if (recoveredCharacter != null) {\n"
    "        _currentCharacterId.value = recoveredCharacter.id\n"
    "    }\n"
    "\n"
    "    return ServiceResult.Success(recoveredAccount)\n"
    "}\n"
)

assert old in content, "recoveredAccount anchor not found"
assert content.count(old) == 1, "anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched GameViewModel.kt: recoveredAccount now uses accountService.accountById() lookup.")
