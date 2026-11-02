---
title: "Get-ADGroupMember : The operation returned because the timeout limit was exceeded"
excerpt: "When using Get-AdGroupMember cmdlet with a group with a large number of members the The operation returned because the timeout limit was exceeded error could be shown. Let's see how to solve this."
last_modified_at: 2026-11-02
categories:
  - PowerShell
  - PowerShell Tips
tags:
  - PowerShell
  - PowerShell from the field
  - PowerShell Active Directory
  - 

toc: true
---

## Get-ADGroupMember - Timeout limit was exceeded

**For nested membership, see [the LDAP membership query]({% post_url 2020-08-12-Get-User-Group-Membership %}). It has different result and scope semantics; it is not an identical replacement for every Get-ADGroupMember call.**
{: .notice--danger}

The *Get-ADGroupMember* cmdlet returns  the members of an Active Directory group. Members can be users, other groups or computers.

It is an handy tool to quickly check if a user has been already been made member of a specific group like for example:

```powershell
# Get all members of the Dl-GroupSame
Get-ADGroupMember -Identity DL-GroupSample
```

```text
distinguishedName : CN=Domain Admins,CN=Users,DC=Lab,DC=com
name              : Domain Admins
objectClass       : group
objectGUID        : 5ccc6037-c2c9-42be-8e92-c8f98afd0011
SamAccountName    : Domain Admins
SID               : S-1-5-21-41432690-3719764436-1984117282-512

distinguishedName : CN=Enterprise Admins,CN=Users,DC=Lab,DC=com
name              : Enterprise Admins
objectClass       : group
objectGUID        : 0215b0a5-aea1-40da-b598-720efe930ddf
SamAccountName    : Enterprise Admins
SID               : S-1-5-21-41432690-3719764436-1984117282-302

distinguishedName : CN=LabAdmin,CN=Users,DC=Lab,DC=com
name              : LabAdmin
objectClass       : user
objectGUID        : ab7c269d-aec5-4fcc-aebe-6cd1a2e6cd53
SamAccountName    : LabAdmin
SID               : S-1-5-21-41432690-3719764436-1984117282-1015
<snip>
```

Issue is when working with large groups with lot of members Domain Controller will cut off the operation the following error will be displayed

```text
Get-ADGroupMember : The operation returned because the timeout limit was exceeded.
At line:1 char:1
+ Get-ADGroupMember DL-LargeGroup
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : OperationTimeout: (DL-LargeGroup:ADGroup) [Get-ADGroupMember], TimeoutException
    + FullyQualifiedErrorId : ActiveDirectoryCmdlet:System.TimeoutException,Microsoft.ActiveDirectory.Management.Comma
   nds.GetADGroupMember
```

A large group can encounter ADWS enumeration limits, but a timeout alone does not prove that limit is the cause. Check DC load, connectivity, query scope and the full error before changing service configuration.

## Solution 1 - Modify Maximum Number of Return Objects

ADWS has a `MaxGroupOrMemberEntries` setting associated with group-member enumeration. Changing domain-controller service configuration is an operational change, not the first troubleshooting step. The original post's configuration-file edit is omitted here: use Microsoft's [ADWS configuration documentation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2008-R2-and-2008/dd391908(v=ws.10)) and your DC change process if investigation identifies that limit as the actual problem.

Do not infer an appropriate new limit from a single group size or copy a value across all DCs without assessing resource impact and testing.

## Solution 2 - Get-ADGroup Cmdlet

Modifying inner Active Directory configuration files is not always a good idea and sometimes not possible at all, for example where I work such a change is not permitted, for this reason I usually workaround the problem not using the *Get-ADGroupMember* cmdlet at all.

The following command reads the group's direct `member` values. These are DNs, potentially for users, computers or nested groups; this does not recursively expand the groups:

```powershell
Get-ADGroup -Identity 'DL-LargeGroup' -Properties Member -ErrorAction Stop | Select-Object -Property 'Member' -ExpandProperty 'Member'
```

Output of the above command can be assigned to a variable and easily manipulated.

This approach has two advantages.

**1.** Modification to Active Directory built-in limits is not required

**2.** Command runs *extremely* fast, for example on a group with over 14k members it took 3 seconds in my environment.

The original three-second timing is a historical observation from my environment. Read performance and result completeness still depend on directory scope and server behavior. Primary-group membership is not represented by ordinary `member` values, and resolving foreign security principals requires additional work. Keep these limits in mind when using the result for an access report.
