# Task 2: n8n Automation

## Objective

The objective of this task was to build a no-code automation workflow using n8n that connects with the database and automates duplicate detection.

## Automation Workflow

The workflow performs the following steps:

1. Receives new data through a Webhook trigger.
2. Sends the received data for processing.
3. Checks the incoming person details against existing database records.
4. Identifies duplicate entries.
5. Sends an alert notification when duplicate records are detected.

## n8n Nodes Used

- Webhook Node
- HTTP Request Node
- Code Node (JavaScript)
- IF Condition Node
- Email Notification Node

## Workflow Flow

Webhook  
↓  
HTTP Request  
↓  
JavaScript Processing  
↓  
Duplicate Check Condition  
↓  
Send Email Alert

## Implementation

The automation was created using n8n and exported as a JSON workflow file.

The workflow accepts new CSV/person data, compares it with existing records, and triggers an alert for duplicate entries.

## Files Included

- workflow/consultbae_duplicate_automation.json
- screenshots/workflow.png
- screenshots/execution.png

## Result

Successfully created and tested an n8n automation workflow for duplicate detection and notification.