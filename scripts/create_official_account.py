
"""
Create the official CineVault account.

The password is entered privately using getpass.
Only its Argon2id hash is stored in MariaDB.
"""

from getpass import getpass

from db.authentication import create_user, authenticate_user


def main():

    print("\nCINEVAULT SETUP Official Account")
  
    username = input("Choose your username: ").strip()

    password = getpass("Choose your password: ")
    confirm_password = getpass("Confirm your password: ")

    if password != confirm_password:
        print("\nPasswords do not match.")
        return

    try:
        # Create the account
        user = create_user(username, password)

        print("\nOfficial account created successfully!")
        print(f"Username: {user['username']}")
        print(f"User ID: {user['user_id']}")

        # Verify successful login
        authenticated_user = authenticate_user(
            username,
            password
        )

        if authenticated_user:
            print("Login verification: PASSED")

        # Verify incorrect passwords are rejected
        invalid_login = authenticate_user(
            username,
            password + "_incorrect"
        )

        if invalid_login is None:
            print("Incorrect password verification: PASSED")

    except ValueError as error:
        print(f"\nAccount creation failed: {error}")


if __name__ == "__main__":
    main()
