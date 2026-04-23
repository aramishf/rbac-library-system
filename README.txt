Part 1 and 2: AAA with RBAC

Provisioning Process
The system handles registration through a specific endpoint where users submit their username, password, and the role they are requesting, such as student, librarian, or admin. Once submitted, the backend generates a random UUID hex string to act as a cryptographic salt. It then combines the password with this salt and hashes it using the SHA-256 algorithm. The user's information is then saved into a JSON flat file. If someone registers for a librarian or admin role, the system flags their account as pending so that an existing admin has to approve them before they can log in.

Authentication Process
For logging in, the system uses SHA-256 along with a unique random salt assigned to each individual user. The main strength of this approach is that the salt completely prevents rainbow table attacks. Even if two different users happen to choose the exact same password, their final hashes will look entirely different in the database because their salts are different. A weakness of this setup is that SHA-256 is designed to be computationally fast. While it works for our library system, in a real-world environment, a fast algorithm is more vulnerable to brute-force attacks compared to slower hashing algorithms like bcrypt. During login, the app simply pulls the user's stored salt, hashes the password they just typed in, and checks if it matches the stored hash.

Authorization Process and Model
I set up the library system using a Role-Based Access Control model. The three roles are student, librarian, and admin, and the available permissions are borrowing books, managing books, and managing users. The mapping is straightforward: students can only borrow books, librarians can borrow and manage books, and admins have access to all three permissions. To enforce this, I wrote a custom Python decorator that checks the active session to see if the user's assigned role contains the required permission for the page they are trying to access. As mentioned earlier, higher-level roles require an admin approval step to prevent anyone from just creating an admin account and taking over the system.

Part 3: Reflection

What was the most intellectually compelling part of the project, and why?
The most interesting part of the project was figuring out how to actually map the theoretical RBAC concepts into working Python code. It is one thing to draw out roles for a library, but figuring out how to build a decorator that dynamically checks a user's permissions before loading a specific webpage was a fun challenge. It really made me think about the principle of least privilege and how to enforce it at the routing level without writing repetitive code everywhere.

How might you be able to apply what you learned in this project in the future?
Understanding how Authentication, Authorization, and Accounting work together is something I am going to use in almost any software project I build from here on out. Knowing exactly why passwords need to be salted and understanding the trade-offs between different hashing algorithms like SHA-256 versus bcrypt will help me make better security decisions when setting up databases. Building the UI to manage these states also gave me a much better idea of how security impacts the actual user experience.

What did you learn from this project?
I learned how to build a functional AAA pipeline from scratch. Instead of relying on a pre-built library that hides the details, I actually had to write the logic for secure user provisioning, salt generation, cryptographic hashing, and role-based access control. I also learned how to use simple JSON files as a lightweight database to store this state.

Which part of this project was the most challenging or difficult?
The hardest part was definitely handling the state of user approvals. I had to write careful logic to make sure a user could successfully create an account but still be securely locked out during the authentication phase until an admin approved them. Handling the edge case for the very first admin user was tricky, as I had to make sure the system didn't accidentally deadlock itself by waiting for an admin approval when no admins existed yet.
