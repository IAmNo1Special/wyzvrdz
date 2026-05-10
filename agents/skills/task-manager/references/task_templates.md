# Task Templates

This reference provides common task templates for different use cases.

## Software Development

### Feature Development
- Design feature specification
- Implement core functionality
- Write unit tests
- Write integration tests
- Update documentation
- Code review
- Deploy to staging
- Deploy to production

### Bug Fix
- Reproduce the bug
- Identify root cause
- Implement fix
- Write regression test
- Verify fix
- Deploy hotfix

### Code Review
- Review code changes
- Check for security issues
- Verify test coverage
- Check documentation
- Provide feedback
- Approve or request changes

## Research

### Literature Review
- Search for relevant papers
- Read and summarize papers
- Identify key themes
- Find research gaps
- Create bibliography

### Experiment Design
- Define hypothesis
- Design experiment methodology
- Prepare data
- Set up environment
- Run pilot test

### Data Analysis
- Collect data
- Clean data
- Analyze data
- Visualize results
- Interpret findings
- Write report

## Project Management

### Planning
- Define project scope
- Create timeline
- Identify dependencies
- Allocate resources
- Set milestones

### Meeting
- Prepare agenda
- Schedule meeting
- Send invitations
- Take notes
- Follow up on action items

### Documentation
- Create outline
- Write content
- Review and edit
- Publish documentation
- Gather feedback

## Personal

### Daily Tasks
- Check email
- Review calendar
- Prioritize tasks
- Complete high-priority items
- Prepare for tomorrow

### Learning
- Set learning goal
- Find resources
- Study material
- Practice skills
- Assess progress

### Health
- Schedule exercise
- Plan meals
- Track sleep
- Schedule checkup
- Review health metrics

## Using Templates

When creating a task list, you can use these templates as starting points:

```bash
# Create a list for a feature
python scripts/create_list.py --name "feature-auth" --description "Authentication feature tasks"

# Add template tasks
python scripts/add_task.py --list "feature-auth" --content "Design feature specification" --priority high
python scripts/add_task.py --list "feature-auth" --content "Implement core functionality" --priority high
python scripts/add_task.py --list "feature-auth" --content "Write unit tests" --priority medium
python scripts/add_task.py --list "feature-auth" --content "Write integration tests" --priority medium
python scripts/add_task.py --list "feature-auth" --content "Update documentation" --priority low
```

## Customizing Templates

Adapt templates to your specific needs:

- Add domain-specific tasks
- Adjust priorities based on context
- Break down tasks further if needed
- Remove irrelevant tasks
- Combine templates for complex projects
