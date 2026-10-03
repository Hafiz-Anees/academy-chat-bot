# Quantiro Customer Lead Capture

## 1. Purpose

Quantiro currently uses a simple lead-capture process for customers and students who are interested in its offerings.

The chatbot collects four required pieces of information:

1. Name
2. Email address
3. Phone number
4. Interest type

## 2. Interest Types

The customer can register their interest in:

* **Course**
* **AI Automation Service**
* **Marketing Service**

The chatbot should store the selected interest type exactly as provided by the available options.

## 3. Lead Information

The current lead form collects:

| Field         | Description                                         |
| ------------- | --------------------------------------------------- |
| Name          | Customer's name                                     |
| Email         | Customer's email address                            |
| Phone Number  | Customer's phone number                             |
| Interest Type | Course, AI Automation Service, or Marketing Service |

No additional lead fields should be required unless the system is updated.

## 4. Database Storage

After the customer submits the form, the collected information is stored in the application's database.

The chatbot must not claim that a lead has been successfully stored unless the database operation actually succeeds.

If the database operation fails, the chatbot must not tell the customer that registration was successful.

## 5. Email Notifications

After a successful registration, email notifications are sent regarding the customer's selected interest.

The notification should correspond to what the customer registered for:

* Course registration → course-related notification
* AI Automation Service registration → AI automation service-related notification
* Marketing Service registration → marketing service-related notification

The chatbot must not claim that an email was successfully sent unless the email-sending system confirms successful delivery/submission.

## 6. Registration Flow

The current registration flow is:

1. Ask for the customer's **name**.
2. Ask for the customer's **email address**.
3. Ask for the customer's **phone number**.
4. Ask what they are interested in:

   * Course
   * AI Automation Service
   * Marketing Service
5. Store the submitted information in the database.
6. Send the appropriate email notification.
7. Confirm the registration to the customer only after the required system operations succeed.

## 7. Validation

The system should validate the submitted information before storing it.

At minimum:

* Name should not be empty.
* Email should follow a valid email format.
* Phone number should not be empty.
* Interest type must be one of the supported options.

Invalid or incomplete submissions should not be treated as successful registrations.

## 8. Security Rules

The system must:

* Protect stored customer information.
* Never expose customer information to unauthorized users.
* Never expose database credentials.
* Never expose email-service credentials.
* Never request passwords or unrelated sensitive information.
* Never include secret keys or credentials in customer-facing messages.
* Follow the application's configured security and access controls.

## 9. Accuracy Rules

The chatbot must:

* Collect only the four currently defined fields.
* Not invent additional registration requirements.
* Not claim that registration succeeded when the database operation failed.
* Not claim that an email was sent when the email operation failed.
* Not invent email addresses or contact details.
* Not modify the customer's submitted information without an appropriate system rule.
* Clearly communicate when registration cannot be completed because of a system error.

## 10. Example Registration

### Customer

I want to register for a course.

### Chatbot

Sure. Please provide your name.

### Customer

Ali Khan

### Chatbot

Please provide your email address.

### Customer

[ali@example.com](mailto:ali@example.com)

### Chatbot

Please provide your phone number.

### Customer

03001234567

### Chatbot

What are you interested in?

* Course
* AI Automation Service
* Marketing Service

### Customer

Course

### Chatbot

Your registration has been submitted successfully.

The information has been stored and the relevant notification has been processed.

## 11. Information Boundary

This document defines the current lead-capture process.

The current system collects only:

**Name + Email + Phone Number + Interest Type**

Any additional fields, lead qualification questions, CRM integrations, automated follow-ups, appointment scheduling, or other lead-management features must be explicitly added to the knowledge base before the chatbot presents them as available functionality.
