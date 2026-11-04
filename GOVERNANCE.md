# Agent Skills Governance

**Adopted** November 4, 2026

Agent Skills is a lightweight, open format for extending AI agent capabilities with specialized knowledge and workflows. The project maintains the specification, its documentation at agentskills.io, and a reference validation library. This document describes how the project is organized, who makes which decisions, and how people join and leave each role.

## 1. General Project Policies

Agent Skills will be established as Agent Skills a Series of LF Projects, LLC. Policies applicable to Agent Skills and participants in Agent Skills, including guidelines on the usage of trademarks, are located at [https://www.lfprojects.org/policies/](https://www.lfprojects.org/policies/). Governance changes approved as per the provisions of this governance document must also be approved by LF Projects, LLC.

Agent Skills participants acknowledge that the copyright in all new contributions will be retained by the copyright holder as independent works of authorship and that no contributor or copyright holder will be required to assign copyrights to the project.

Except as described below, all code and specification contributions to the project must be made using the Apache License, Version 2.0 (available here: [https://www.apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)) (the "Project License").

All outbound code and specifications will be made available under the Project License. The Core Maintainers may approve the use of an alternative open license or licenses for inbound or outbound contributions on an exception basis.

All documentation (excluding specifications) will be made available under Creative Commons Attribution 4.0 International license, available at: [https://creativecommons.org/licenses/by/4.0](https://creativecommons.org/licenses/by/4.0).

The LF Projects Code of Conduct and the LF Projects Antitrust Policy apply to everyone who takes part in the project.

## 2. Technical Governance

The project adopts a hierarchical structure, similar to the Model Context Protocol, Python, PyTorch, and other open source projects.

| Role | Scope |
| --- | --- |
| **Lead Maintainers** | Final decision authority |
| **Core Maintainers** | The specification and overall project direction |
| **Maintainers** | Documentation, the reference library, and other components |
| **Contributors** | Issues, pull requests, and discussions |

The Lead Maintainers and the Core Maintainers together form the **Agent Skills Technical Steering Committee** (the "TSC"). The TSC is responsible for the technical direction of the project. The voting members of the TSC are the Lead Maintainers and Core Maintainers listed in MAINTAINERS.md.

All maintainers are expected to have a strong bias toward the design philosophy of Agent Skills, which favors a small specification and a high bar for additions. Membership in technical governance is for individuals, not companies. No seats are reserved for specific companies, and membership stays with the person when that person changes employers.

Core Maintainers will be drawn from more than one organization. When Core Maintainers are appointed, the Lead Maintainers and Core Maintainers consider whether the group reflects the breadth of the Agent Skills ecosystem, including the organizations that ship production implementations of the format.

## 3. Roles

### Contributors

Anyone who files an issue, opens a pull request, or takes part in a discussion is a Contributor. There are no formal requirements.

### Maintainers

Maintainers steward a specific area, such as the documentation site, the client showcase, or the reference library. They make decisions for their area independently and escalate to the Core Maintainers when needed. Maintainers have write access to the areas they maintain and are appointed by the Core Maintainers. An area that has no Maintainer is the responsibility of the Core Maintainers.

Maintainers will review requests for a listing on the client showcase against the criteria published in the contributing guide, which will apply in the same way to every applicant. An applicant will be able to ask the Core Maintainers to review a refusal.

### Core Maintainers

Core Maintainers steer the specification and the overall direction of the project. They decide on substantive changes to the specification under section 5, approve releases of the specification, resolve disputes, and appoint or remove Maintainers. They can veto a Maintainer decision by majority vote of all Core Maintainers. Core Maintainers have write access to the project's repositories and use the same pull request workflow as outside contributors.

### Lead Maintainers

Lead Maintainers are the final decision makers. They hold final authority and can veto any decision by the Core Maintainers or the Maintainers. They appoint and remove Core Maintainers and are administrators on all project infrastructure. Lead Maintainers are part of the Core Maintainer group and are expected to state their reasoning publicly when they exercise a veto or decide a disagreement escalated to them. A Lead Maintainer is a Core Maintainer for as long as that person is a Lead Maintainer, and is counted wherever this document refers to all Core Maintainers or to a vote or majority of the Core Maintainers.

## 4. Decision Process

Decisions are made at the lowest appropriate level. Maintainers handle day-to-day decisions within their area. Core Maintainers act on escalations, on matters that cut across areas, and wherever this document requires their approval. Lead Maintainers step in on contested governance decisions or when the Core Maintainers cannot reach consensus.

The TSC decides by consensus wherever possible. Where consensus cannot be reached, the Core Maintainers decide by a majority vote of all Core Maintainers, subject to a veto by any Lead Maintainer.

The TSC meets as needed to discuss and vote on proposals, and may decide matters in writing between meetings.

| Issue | First escalation | Second escalation |
| --- | --- | --- |
| Technical disagreement in a pull request | Maintainer for the area | Core Maintainers |
| Disagreement with a Maintainer decision | Core Maintainers | Lead Maintainers |
| Disagreement among Core Maintainers | Lead Maintainers | None |
| Code of conduct report | Core Maintainers | Lead Maintainers |
| Security issue | Core Maintainers | Lead Maintainers |

The person or group to whom a matter is escalated provides binding guidance, requests more information, or escalates the matter further if needed. A code of conduct report may always be made to LF Projects as the LF Projects Code of Conduct provides.

## 5. Changes to the Specification

The project keeps a high bar for additions to the specification. As the contributing guide puts it, "it is much easier to add things to a specification than to remove them." Proposals should address real implementation challenges, not theoretical concerns.

Bug fixes, typo corrections, clarifications and new examples are made by ordinary pull requests. Any other change to the specification, including one that adds, removes or alters normative behavior, is a substantive change and requires the approval of the Core Maintainers under section 4. Where it is unclear whether a change is substantive, the Core Maintainers decide. Once the project has a numbered Specification Proposal track, a substantive change will require a numbered Specification Proposal, which will move through the following steps:

1. **Proposal.** The author opens a pull request that adds the proposal as a file in the repository. The proposal states the problem, the change to the specification, the reasoning, the effect on existing skills and clients, and any security implications.

2. **Sponsor.** A Maintainer or Core Maintainer agrees to sponsor the proposal and guides it through review. A proposal that finds no sponsor within six months becomes dormant and can be revived later.

3. **Review.** Discussion takes place in public on the pull request. The author is responsible for building consensus and recording dissenting views.

4. **Decision.** The Core Maintainers accept or reject the proposal under the decision process in section 4.

5. **Final.** An accepted proposal becomes final when the specification text is merged and at least one working implementation demonstrates the change.

Releases of the specification will be tagged and will carry a changelog, so that implementers can declare and test against a specific version.

## 6. TSC Representative

The Lead Maintainers designate one member of the TSC as its TSC Representative under the Agentic AI Foundation Charter and tell the Governing Board of the Agentic AI Foundation who that person is. If the TSC Representative stops contributing actively or leaves the project, the Lead Maintainers will designate a replacement within sixty days.

## 7. Communication

Questions and early ideas are raised in GitHub Discussions, and concrete bugs are filed as GitHub Issues. The project also maintains a public Discord server for open conversation. The project may keep private channels for certain communications, including security reports and code of conduct matters. Except for matters handled in those channels, decisions and the discussion that supports them must be recorded on GitHub.

## 8. Criteria for Becoming a Maintainer

Membership in the maintainer groups is given to individuals on a merit basis. The criteria in this section are the ones the project applies to every candidate, whoever employs them.

### Maintainer

A candidate for Maintainer is expected to show each of the following:

- **Sustained contribution.** High-quality contributions to the project over at least three months, such as merged pull requests, reviews, issue triage, or documentation.

- **Knowledge of the area.** Working knowledge of the area the candidate would maintain and of the specification as a whole.

- **Independence.** The ability to put the interests of the project and its users ahead of those of any single employer or organization.

- **Conduct.** Constructive, respectful participation consistent with the LF Projects Code of Conduct.

- **Availability.** The time to review contributions and respond to escalations in the area.

### Core Maintainer

A candidate for Core Maintainer is expected to meet the Maintainer criteria and to show each of the following:

- **Sustained contribution at depth.** At least six months of substantial contribution to the specification, to the project as a Maintainer, or to a production implementation of the format.

- **Judgment.** Demonstrated good judgment on decisions that affect the whole project, shown, for example, in reviews of Specification Proposals.

- **Trust across organizations.** The trust and respect of contributors from more than one organization.

- **Restraint.** A commitment to the long-term health of the format and to restraint in how the specification evolves.

- **Participation.** The capacity to attend TSC meetings, vote, and take part in governance.

The Core Maintainer group is kept small on purpose, so that the project keeps a coherent technical direction. Meeting the criteria makes a person eligible and does not by itself entitle that person to a seat.

### Composition of the Core Maintainer group

When a Core Maintainer seat is filled, the people making the decision also weigh the composition of the group as a whole. They consider the following:

- Whether the group reflects the breadth of the Agent Skills ecosystem, including the organizations that ship production implementations of the format and the people who author skills.

- Whether the group draws on more than one organization.

- Whether the group remains small enough to decide by consensus.

These factors guide the choice among qualified candidates. They do not reserve a seat for any organization.

### Initial appointments

The initial Lead Maintainers and Core Maintainers, and any Maintainers named at adoption, are listed in MAINTAINERS.md when this document is adopted. The time periods in this section and the steps in section 9 do not apply to the initial appointments.

## 9. Nominating, Confirming and Removing Maintainers

Membership is associated with the person, not the employer, and has no term limit.

| Role | How a person is appointed |
| --- | --- |
| Maintainer | Sponsored by a Maintainer or Core Maintainer and approved by the Core Maintainers |
| Core Maintainer | Endorsed by a majority of all Core Maintainers and approved by the Lead Maintainers, or appointed directly by the Lead Maintainers |
| Lead Maintainer | Named at adoption of this document and afterward only by succession under section 10 |

A person may nominate themselves or be nominated by a sponsor. A person who nominates themselves must still secure the sponsorship or endorsement that the table above requires for the role. A nomination moves through the following steps:

1. **Nomination.** The nominee or sponsor opens an issue in the repository. The issue links to the contributions that show the criteria in section 8 are met.

2. **Community review.** The nomination is open for community comment.

3. **Decision.** The approving body decides and records its decision on the issue. A direct appointment by the Lead Maintainers is recorded in the same way.

4. **Onboarding.** The new role holder receives the access that goes with the role and is added to MAINTAINERS.md.

A Maintainer or Core Maintainer who has not taken part in the project for six months may be moved to emeritus status after review, by the Core Maintainers for a Maintainer and by the Lead Maintainers for a Core Maintainer. Anyone may step down at any time. A role may be revoked for a code of conduct violation or sustained non-participation. The reasons for a removal are recorded, except where a code of conduct matter requires confidentiality.

## 10. Succession

If a Lead Maintainer leaves the role for any reason, succession begins on that person's written notice. If the Lead Maintainer cannot give notice, the remaining Lead Maintainers or the Core Maintainers may determine that the Lead Maintainer is unable to continue serving.

If one or more Lead Maintainers remain, they appoint a successor, by majority vote if more than one remains, and they continue to govern until a successor is appointed.

If no Lead Maintainers remain, the Core Maintainers appoint a successor by majority vote of all Core Maintainers within 30 days. Until a new Lead Maintainer is appointed, the project operates by a two-thirds vote of all Core Maintainers.

## 11. Amendment

Amendments to this document may be proposed only by the Lead Maintainers. A proposed amendment must be approved by a two-thirds majority of all Core Maintainers and by LF Projects, LLC to take effect, subject to a veto by any Lead Maintainer. An amendment proposal must meet the following requirements:

1. It is submitted in writing with a clear rationale.

2. It includes the specific language that would change.

3. It is open for comment for at least five days before the vote.

4. It is decided by a recorded vote of the Core Maintainers.

Updates to MAINTAINERS.md that record who holds a role are not amendments to this document.

## 12. Current Role Holders

The current Lead Maintainers, Core Maintainers, Maintainers and TSC Representative are listed in MAINTAINERS.md.

Portions of this document are adapted from the [Governance and Stewardship document](https://modelcontextprotocol.io/community/governance) and the [Contributor Ladder](https://modelcontextprotocol.io/community/contributor-ladder) of the Model Context Protocol project, which that project makes available under the [Creative Commons Attribution 4.0 International license](https://creativecommons.org/licenses/by/4.0/).
