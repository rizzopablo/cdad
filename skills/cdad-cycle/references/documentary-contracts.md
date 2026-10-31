# Documentary contracts

Shared norm for the engagements whose product is a document: discovery notes,
process maps and user stories. The roles cite this file and state their own
obligation in their own words; no other surface reproduces this wording. It
applies when an engagement declares a documentary product — code work keeps the
rules of its own role.

## 1. The four categories

Every claim of the product falls into one of these four categories. They are a
mandatory criterion, not a format: they may be distinguished with headings,
labels, columns or unambiguous wording, and an engagement may impose a more
specific shape when that shape is part of its observable promise. Empty
sections and invented instances are never required to fill a template.

**Evidence.** A claim of evidence names the source that backs it and the
locator where that source can be examined. Evidence does not attribute to the
source more than it demonstrates: a document never supports a conclusion it
does not prove.

**Proposal.** A proposal is an alternative of the author and is presented as
such: it is not an observed fact and not an approved decision. A reader must be
able to tell it apart from both.

**Contradiction.** With two incompatible claims, each position keeps its own
reference and no consensus is invented: neither position is deleted without an
accredited decision.

**Pending.** A pending item states what is missing and what information or
decision would resolve it. It does not turn silently into a fact: the gap is
declared as a gap.

The categories describe claims and questions, not whole documents. A
contradiction may originate a pending item; keeping them apart does not force
the same content to be written twice.

## 2. Minimum locator per source type

Every backing allows the examined source and the fragment used to be recovered.
The minimum locator depends on the source type:

| Source type | Minimum locator |
|---|---|
| Repository file | Relative path, lines or section or unambiguous internal identifier, and the revision or snapshot examined |
| Markdown input or text received as a document | Path or identifier of the input, section or lines or unambiguous fragment, and the version or snapshot examined |
| Message or decision of the user | Recoverable identifier of the message or of the authorized transcript, date or sufficient context, and the fragment or section at stake |
| Minutes or transcript | Identifier and version of the input, and the section, turn or timestamp at stake |
| Web page or any other mutable source | Original URL, internal location, and a recoverable version or capture with its consultation or capture date |

The version may be declared once in a source inventory and reused by
identifier; it need not be repeated in every citation. A live URL with its
consultation date, without the content examined, is not enough as backing.

An external source needs a representation reachable inside the authorized
scope; this norm never grants extra access to any source. If the source cannot
be recovered, or does not support the claim, the backing is not accredited:
the reference is corrected, the claim is reformulated, or a pending item is
declared.

## 3. Pending classification

Each pending item records the question at stake, the affected location, the
information or decision needed to resolve it, its closure condition and a
justified classification. It identifies the decision-maker or responsible party
when that is known; otherwise it declares that the designation is still
missing.

A pending item is blocking when it prevents verifying a postcondition or an
acceptance criterion of the current contract. It is also blocking, for example,
when a fact the committed result depends on is left without backing, when a
decision needed to bound the product or to protect its inputs is absent, or
when a verification the engagement committed cannot be run. An item whose
effect on an obligation of the contract is still unknown is blocking as well:
not knowing the effect is no evidence that no obligation is touched.

A pending item is non-blocking when it lies outside the scope of the
commitment, or when the contract promises to present the uncertainty instead of
resolving it.

A contradiction may stay open only when the promise is to document divergent
positions. It must be resolved when what was promised is an unambiguous
operative definition that rests on it.

The producer never downgrades an obligation to non-blocking unilaterally. If a
promise must be given up, the contract changes through the approval procedure
in force.

## 4. The four declarations of an engagement

Every engagement with a documentary product identifies, before starting:

1. The authorized sources: which inputs may be read and which may not.
2. The editable product, through delimited paths.
3. The verifiers and the protected acceptance inputs.
4. The expected evidence and the verification limits.

The editable product is expressed as a directory of its own, declared in the
scope of the engagement. An exact documentary path is admitted only when the
path policy already declares it. These declarations use the fields the
engagement already carries: no new field is added for them.

### What GREEN may not edit

The sources, the acceptance contract, the verifiers and the templates used as
an oracle stay outside the editable scope of GREEN. Sharing the `docs`
classification does not turn a file into the editable product. If the editable
product overlaps a source, the acceptance contract, a verifier or a template,
or if it is unclear which part a file plays — product, source, verifier or
acceptance input — the engagement is ambiguous: that part is stopped and the
engagement is corrected before continuing.

### The producer does not modify its oracle

The producer does not modify its oracle. A legitimate change of the oracle
returns to the competent role and, when it alters the contract, returns to the
approval in force. It is never made from GREEN to obtain a favourable result:
when the required result forces the oracle to change, that part stops and is
reported.

## 5. Documentary boundaries per role

**Orchestrator.** It prepares the four declarations, delimits the scopes of
sources and product, and checks in the existing gates that the declared evidence
exists and that each pending item carries its classification. It adds no gate,
role or permission to achieve that.

**Architect.** It specifies verifiable promises, the admitted sources, the
limits of that verification and the acceptance criterion. It returns its
proposal as a draft: it does not write the product and does not approve its own
text.

**Test-writer.** It derives its verifier from the contract and the authorized
inputs, never from the produced document it has to verify, and it edits only the
authorized tests. If the contract is not enough to write the oracle, it reports
that instead of reading the product.

**Implementer.** It produces only the documentary product explicitly authorized
by the contract, inside the declared paths, and it does not edit the sources,
the verifiers or the protected inputs. The prohibition on editing tests is kept
as it stands, for code and for the document alike.

**Reviewer.** In an independent, read-only session it contrasts the product
with its contract and with the sources, and records findings, limits and
abstentions. It never turns the presence of a structure into proof of fidelity.

**Scribe.** It keeps its Memory Bank function: its drafts are written from the
evidence of the closure, and it does not assume the general documentary
production and does not approve that product.

## 6. Two records that never replace each other

The closure keeps two separate records:

- **Automatic or structural control:** which check ran, its result, the scope
  it covers and its limitations.
- **Independent semantic review:** which claims and which sources were
  examined, the result, the findings and the limitations or abstentions.

The presence of sections, labels, files or resolvable references does not
demonstrate fidelity, sufficiency or semantic truth. A transport receipt, or
the structural acceptance of the packet, does not accredit a semantic review.
A textual obligation or a packet is not a sandbox: it does not demonstrate the
absence of transient writes.

## 7. Contrast and acceptance

Each claim is contrasted with its source, looking for three defects:
insufficient backing, omitted contradictions, and references that exist but do
not support what is claimed. The review declares its real scope — what it
examined and what it did not — and promises no infallible detection.

The functional acceptance belongs to the user or owner who approves, once the
committed verifications are done. Acceptance is not requested while a pending
item prevents the contract from being accredited. Admissible pending items stay
visible in the closure record.

## 8. Scope of this norm

This file is the single house of the documentary norm. The roles, the packet
blocks and the agents that consume it point to it by file name and state their
obligation without copying these phrases.

This norm creates no role, stage or permission, does not replace the Memory
Bank and does not turn the scribe into a general documentary producer. Its
application is conditional: it governs when the engagement has a documentary
product. The rule that whoever produces does not modify its oracle already
governed code and is kept unchanged here.
