# Migration Review — enablement-aws-serverless

Auto-generated. Check boxes as you resolve. The repo already passed `mkdocs build --strict` at generation.

## 0. Context (read once)
- Labs: 5  |  Total duration in source: 10 min
- Authors carried over: none
- Environment model: DOCS-FIRST (no cloud provisioning; prose references the learner's own cloud account).
- Lab → page map:
    - aws-lab0 immersion-day → docs/1-aws-lab0-immersion-day.md (id: aws-lab0 immersion-day, 15 images)
    - aws-lab6 → docs/2-aws-lab6.md (id: aws-lab6, 11 images)
    - aws-lab7 → docs/3-aws-lab7.md (id: aws-lab7, 20 images)
    - aws-lab11-serverless → docs/4-aws-lab11-serverless.md (id: aws-lab11-serverless-setup, 12 images)
    - aws-lab12-serverless observability → docs/5-aws-lab12-serverless-observability.md (id: aws-lab12-serverless observability, 14 images)

## 1. Blocking — must resolve before committing the branch  (2 items)
- [ ] docs/3-aws-lab7.md:234 — Auto-converted aside with images/multiple paragraphs; verify admonition body renders correctly.
- [ ] docs/3-aws-lab7.md:295 — Auto-converted aside with images/multiple paragraphs; verify admonition body renders correctly.

## 2. Environment (cloud-account prose) — confirm docs-first wording  (4 items)
- [ ] docs/1-aws-lab0-immersion-day.md — References a cloud account/portal ('aws console'); confirm docs-first wording (learner uses their own account).
- [ ] docs/2-aws-lab6.md — References a cloud account/portal ('aws console'); confirm docs-first wording (learner uses their own account).
- [ ] docs/4-aws-lab11-serverless.md — References a cloud account/portal ('aws console'); confirm docs-first wording (learner uses their own account).
- [ ] docs/5-aws-lab12-serverless-observability.md — References a cloud account/portal ('aws console'); confirm docs-first wording (learner uses their own account).

## 3. Run & re-capture (validates technical accuracy)  (5 items)
- [ ] docs/1-aws-lab0-immersion-day.md — Run this lab and verify its 15 screenshots are current (technical-accuracy gate).
- [ ] docs/2-aws-lab6.md — Run this lab and verify its 11 screenshots are current (technical-accuracy gate).
- [ ] docs/3-aws-lab7.md — Run this lab and verify its 20 screenshots are current (technical-accuracy gate).
- [ ] docs/4-aws-lab11-serverless.md — Run this lab and verify its 12 screenshots are current (technical-accuracy gate).
- [ ] docs/5-aws-lab12-serverless-observability.md — Run this lab and verify its 14 screenshots are current (technical-accuracy gate).

## 4. Alt-text review (batch-approvable)  (74 items)
- [ ] docs/1-aws-lab0-immersion-day.md:37 — Alt text auto-derived ('WelcometoDT') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:49 — Alt text auto-derived ('event engine initial screen') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:53 — Alt text auto-derived ('one time password') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:57 — Alt text auto-derived ('send passcode') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:61 — Alt text auto-derived ('enter passcode') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:65 — Alt text auto-derived ('aws event engine') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:69 — Alt text auto-derived ('aws event engine popup') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:73 — Alt text auto-derived ('setup aws portal') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:89 — Alt text auto-derived ('lab2 change region') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:98 — Alt text auto-derived ('setup cloud shell icon') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:102 — Alt text auto-derived ('lab2 cloudshell splash page') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:106 — Alt text auto-derived ('setup cloud shell') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:146 — Alt text auto-derived ('dt provision dashboard list') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:150 — Alt text auto-derived ('dt copy command') — confirm it reads sensibly.
- [ ] docs/1-aws-lab0-immersion-day.md:194 — Alt text auto-derived ('CFTCreateCompeleteMonoAG') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:54 — Alt text auto-derived ('lab2 setup') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:87 — Alt text auto-derived ('setup cloudformation search') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:95 — Alt text auto-derived ('setup cloudformation stacks') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:99 — Alt text auto-derived ('setup cloudformation stacks details') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:107 — Alt text auto-derived ('setup stack complete') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:115 — Alt text auto-derived ('setup eks cluster') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:119 — Alt text auto-derived ('setup eks cluster detail') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:186 — Alt text auto-derived ('lab4 operator menu') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:194 — Alt text auto-derived ('lab4 operator new') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:253 — Alt text auto-derived ('mz pick all') — confirm it reads sensibly.
- [ ] docs/2-aws-lab6.md:257 — Alt text auto-derived ('lab2 eks hosts') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:105 — Alt text auto-derived ('lab2 k8s namespaces') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:182 — Alt text auto-derived ('lab2 k8s layers') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:188 — Alt text auto-derived ('lab4 aks nodeutiliz') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:193 — Alt text auto-derived ('lab4 aks workload') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:195 — Alt text auto-derived ('lab4 aks workload filter') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:199 — Alt text auto-derived ('la4 aks kubeworkload') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:202 — Alt text auto-derived ('lab4 aks frontend workload') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:206 — Alt text auto-derived ('lab4 aks pod') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:214 — Alt text auto-derived ('lab4 aks container') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:220 — Alt text auto-derived ('aks layer7 service') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:241 — Alt text auto-derived ('lab2 step8 services') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:243 — Alt text auto-derived ('lab4 k8 mgmtzone filter') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:245 — Alt text auto-derived ('lab4 k8 service filter') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:248 — Alt text auto-derived ('lab4 k8 service view mod') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:258 — Alt text auto-derived ('lab4 k8 service backflow') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:267 — Alt text auto-derived ('lab2 step8 services') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:269 — Alt text auto-derived ('lab4 k8 mgmtzone filter') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:271 — Alt text auto-derived ('lab4 k8 frontendservice filter') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:273 — Alt text auto-derived ('lab4 serviceflow') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:281 — Alt text auto-derived ('lab4 serviceflow responsetime') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:288 — Alt text auto-derived ('lab4 serviceflow thoroughput') — confirm it reads sensibly.
- [ ] docs/3-aws-lab7.md:307 — Alt text auto-derived ('lab2 picture future') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:57 — Alt text auto-derived ('19 Lambda 1') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:62 — Alt text auto-derived ('serverlesswebsite') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:65 — Alt text auto-derived ('serverlesscronjob') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:68 — Alt text auto-derived ('serverlessevents') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:71 — Alt text auto-derived ('serverlessfile') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:74 — Alt text auto-derived ('serverlesswebhook') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:80 — Alt text auto-derived ('lab2 picture future') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:108 — Alt text auto-derived ('lambdaAssests2') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:120 — Alt text auto-derived ('lambdaDeploy') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:154 — Alt text auto-derived ('CWLambdas1') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:169 — Alt text auto-derived ('catalog service serverless') — confirm it reads sensibly.
- [ ] docs/4-aws-lab11-serverless.md:179 — Alt text auto-derived ('catalogDeploy') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:8 — Alt text auto-derived ('lambdaServices') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:12 — Alt text auto-derived ('deployLambda') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:19 — Alt text auto-derived ('deployLambdaSettings') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:30 — Alt text auto-derived ('awsLambdaVar') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:35 — Alt text auto-derived ('cwLambdaLink') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:44 — Alt text auto-derived ('serviceFlow') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:48 — Alt text auto-derived ('frontendServiceFlow') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:55 — Alt text auto-derived ('catalogdServiceFlow') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:62 — Alt text auto-derived ('filter') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:66 — Alt text auto-derived ('feDistributedTracing') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:70 — Alt text auto-derived ('catalogDTracing') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:74 — Alt text auto-derived ('trace') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:85 — Alt text auto-derived ('lambdaDT') — confirm it reads sensibly.
- [ ] docs/5-aws-lab12-serverless-observability.md:93 — Alt text auto-derived ('otelDT') — confirm it reads sensibly.

## 5. Judgment calls (does this lab still belong?)  (5 items)
- [ ] docs/1-aws-lab0-immersion-day.md — Confirm this lab still belongs in the migrated workshop.
- [ ] docs/2-aws-lab6.md — Confirm this lab still belongs in the migrated workshop.
- [ ] docs/3-aws-lab7.md — Confirm this lab still belongs in the migrated workshop.
- [ ] docs/4-aws-lab11-serverless.md — Confirm this lab still belongs in the migrated workshop.
- [ ] docs/5-aws-lab12-serverless-observability.md — Confirm this lab still belongs in the migrated workshop.

## 6. Definition of done
- [ ] All boxes above checked
- [ ] `mkdocs build --strict` still clean
- [ ] repos.yaml snippet reviewed (see REVIEW-repos-snippet.yaml) — **do NOT register until the owner lifts the branch-only hold**
- [ ] Work committed to a branch (no PR to main at this time)
