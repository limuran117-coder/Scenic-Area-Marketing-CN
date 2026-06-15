## Description: <br>
Analyzes and rewrites prompts for better AI output, creates reusable prompt templates for marketing use cases, and structures end-to-end AI content workflows. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[alirezarezvani](https://clawhub.ai/user/alirezarezvani) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, prompt engineers, and marketing teams use this skill to improve prompts, evaluate A/B prompt variants, maintain prompt history, and create reusable templates for AI-assisted content workflows. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The optional runner command can execute an external CLI chosen by the user. <br>
Mitigation: Review every --runner-cmd before use and run only approved commands in an appropriate environment. <br>
Risk: Prompt test inputs may include proprietary or customer data that could be sent to an external runner. <br>
Mitigation: Avoid feeding sensitive data to external CLIs unless the tool and data handling path are approved. <br>
Risk: The local prompt history store contains prompt content. <br>
Mitigation: Keep the prompt history file private and avoid committing it unless the contents have been reviewed for disclosure risk. <br>


## Reference(s): <br>
- [Prompt Templates](references/prompt-templates.md) <br>
- [Technique Guide](references/technique-guide.md) <br>
- [Evaluation Rubric](references/evaluation-rubric.md) <br>
- [README](README.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with inline shell commands, prompt templates, JSON test-case structures, and optional text or JSON script output] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [The prompt tester can emit text or JSON metrics; the prompt versioner stores local JSONL prompt history and can emit diffs and changelog output.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence and artifact metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
