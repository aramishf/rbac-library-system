# SJSU Library (SJSUL) Access Control System

## Part 1 & 2: AAA with RBAC

This project implements an Access Control System for a fictitious library (SJSUL) using Python and Flask. The data is stored in "flat files" using the JSON format (`data/users.json` and `data/roles.json`).

### Provisioning
Users can register via the `/register` endpoint.
- **Input:** Username, Password, Requested Role (student, librarian, admin).
- **Process:** The system generates a unique random salt (UUID hex) and hashes the password using SHA-256 (`hashlib.sha256(password + salt)`). The user is added to `users.json`. If the user requests an Admin or Librarian role, their account must be approved by an existing Admin before they can log in.

### Authentication
Users log in via the `/login` endpoint.
- **Hashing Mechanism:** SHA-256 with a unique random salt per user. 
- **Strengths:** Using a salt prevents rainbow table attacks. Even if two users have the same password, their hashes will be completely different because their salts are different.
- **Weaknesses:** SHA-256 is computationally fast. This makes it vulnerable to brute-force and dictionary attacks if an attacker gains access to the database (unlike slow hashing algorithms like bcrypt or Argon2).
- **Process:** The system retrieves the user's stored salt, hashes the input password with that salt, and compares it to the stored hash.

### Authorization (RBAC)
The system uses Role-Based Access Control (RBAC). 
- **Roles:** `student`, `librarian`, `admin`.
- **Permissions:** `borrow_books`, `manage_books`, `manage_users`.
- **Mapping:**
  - `student`: `borrow_books`
  - `librarian`: `borrow_books`, `manage_books`
  - `admin`: `borrow_books`, `manage_books`, `manage_users`
- **Approvals:** A user requesting `admin` or `librarian` roles requires an existing `admin` to approve their account before they can successfully authenticate.

---

## Part 3: Reflection

**1. What was the most intellectually compelling part of the project, and why?**
The most intellectually compelling part of the project was designing the Role-Based Access Control (RBAC) schema and mapping it to practical use cases in the fictitious SJSU Library. Balancing security with usability is a core challenge in Information Security. Determining which roles should have which permissions—for instance, ensuring that a 'student' can only borrow books while a 'librarian' can manage the catalog—required careful thought about the principle of least privilege. Implementing the decorator pattern in Python to enforce these permissions dynamically on web routes was also a very satisfying technical challenge that beautifully bridged the gap between theoretical security models and practical software engineering.

**2. How might you be able to apply what you learned in this project in the future?**
The principles of Authentication, Authorization, and Accounting (AAA) are foundational to almost every modern software application. In the future, whether I am building a small web application or working on enterprise-level enterprise software, I will be able to apply the RBAC models learned here to ensure secure access control. Understanding the strengths and weaknesses of hashing algorithms (like SHA-256 vs. bcrypt) and the critical importance of salting passwords will inform my technical decisions when designing secure user provisioning systems. Furthermore, the experience of building a functional UI to manage these security states gives me a holistic view of full-stack security integration.

**1. What did you learn from this project?**
I learned how to implement a complete AAA pipeline from scratch, including secure user provisioning, cryptographic password hashing with salts, and role-based authorization. I also learned how to use JSON flat files as a lightweight database and how to structure a Flask web application to enforce security policies at the routing level.

**2. Which part of this project was the most challenging or difficult?**
The most challenging part was managing the state and flow of user approvals. Ensuring that a user could successfully provision an account but be securely denied access during authentication until an admin approved them required careful logic. It was critical to handle the edge case of the very first user (the initial admin) so the system didn't deadlock itself.
