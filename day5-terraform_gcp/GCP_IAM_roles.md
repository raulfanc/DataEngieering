### IAM roles that relevant to this project:

- Viewer: This role provides read-only access to all resources within a project. Users with this role can view resources
  and their metadata but cannot modify or delete them. In a real-world application, this role is often given to team
  members who need to monitor project resources but do not need to make any changes.

- Storage Admin: This role grants full control over the Google Cloud Storage resources within a project. Users with this
  role can create, delete, and manage buckets and objects within the project's Cloud Storage. In your project, this role
  is necessary if you're using Cloud Storage as a data lake to store raw or processed data.

- Storage Object Admin: This role provides full control over the objects within a project's Cloud Storage buckets but
  does not grant permission to manage the buckets themselves. Users with this role can create, delete, and manage
  objects within the buckets, but cannot create or delete the buckets. This role is useful when you need to provide
  granular access to data stored in Cloud Storage.

- BigQuery Admin: This role grants full control over BigQuery resources within a project. Users with this role can
  create, delete, and manage BigQuery datasets, tables, and jobs. In your project, this role is necessary if you're
  using BigQuery to process, analyze, and store data.

These roles are essential for your project as they enable you to manage the data stored in your data lake (Cloud
Storage) and work with that data in BigQuery. By assigning appropriate roles to your team members or service accounts,
you can ensure they have the necessary permissions to perform their tasks without granting excessive access.

### APIs that relevant to this project:

also I am asked to enable APIs for this project:

1. Identity and Access Management (IAM) API
2. IAM Service Account Credentials API

Identity and Access Management (IAM) API: The IAM API allows you to manage access control by defining who (identities)
can perform which actions (permissions) on specified resources. By enabling this API, you can programmatically manage
IAM policies, roles, and service accounts in your project.

IAM Service Account Credentials API: This API allows you to create and manage service account keys, which are used for
authentication when interacting with Google Cloud services. By enabling this API, you can programmatically create,
delete, and manage service account keys, as well as generate access tokens and sign JSON Web Tokens (JWTs) for
authentication.

**Question 1**: why do I need to enable this two?
**Answer 1:** You need to enable these two APIs because they provide the necessary functionality to manage access control
and service account credentials within your project. These APIs allow you to automate tasks related to IAM and service
accounts, making it easier to manage your project's security.

**Question 2:** how much does they charge?
**Answer 2:** The IAM API and the IAM Service Account Credentials API are both offered at no additional cost. However, you
should still monitor your overall Google Cloud usage to ensure you stay within your budget. You can find more details on
Google Cloud's pricing page: https://cloud.google.com/pricing

**Question 3:** what services in this GCP project will use these two APIs
**Answer 3:** In your GCP project, any services that require authentication and access control will utilize these APIs. For
example, when you use Google Cloud Storage or BigQuery, you need to authenticate using service account credentials,
which are managed through the IAM Service Account Credentials API. Similarly, when you want to grant or revoke access to
resources in your project, you'll use the IAM API to manage the permissions.

These APIs work behind the scenes to ensure that your project's resources are accessed securely and only by authorized
users or service accounts.