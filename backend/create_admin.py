# create_admin.py - make an Admin account from the command line
#
# This is the ONLY way to get an Admin (like "createsuperuser" in Django).
# The website can only create Staff accounts.
#
# Run it from the project folder (the one that has backend/ and frontend/):
#     python -m backend.create_admin
#
# Optional: give name and email on the command line, the password is always asked:
#     python -m backend.create_admin --name "Om Sai" --email om@example.com

import argparse
import getpass
import sys

from sqlalchemy.exc import OperationalError

from .database import Base, engine, SessionLocal
from . import models                      # needed so the tables are known to Base
from .models import User
from .security import hash_password
from .validation import clean_name, clean_email, check_password_rules


def create_user(db, name, email, password, role):
    """Save a new user. Used by this command (role = Admin)."""
    user = User(
        name=clean_name(name),
        email=clean_email(email),
        password_hash=hash_password(check_password_rules(password)),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def ask(question, check):
    """Ask until the answer passes the check function."""
    while True:
        answer = input(question)
        try:
            return check(answer)
        except ValueError as error:
            print("  " + str(error))


def ask_password():
    while True:
        password = getpass.getpass("Password: ")
        try:
            check_password_rules(password)
        except ValueError as error:
            print("  " + str(error))
            continue

        again = getpass.getpass("Password (again): ")
        if again != password:
            print("  Passwords do not match, try again")
            continue
        return password


def main():
    parser = argparse.ArgumentParser(description="Create a VisionStock Admin account")
    parser.add_argument("--name", help="full name")
    parser.add_argument("--email", help="email address (used to login)")
    args = parser.parse_args()

    try:
        Base.metadata.create_all(bind=engine)      # make the tables if they are missing
        db = SessionLocal()
        db.query(User).first()                     # test the connection now
    except OperationalError as error:
        print("\nCannot connect to the database.")
        print("Check DATABASE_URL in your .env file and make sure the database is running.")
        print("Tip: for a quick test use  DATABASE_URL=sqlite:///visionstock.db\n")
        print("Details:", str(error.orig))
        sys.exit(1)

    try:
        # ---- name and email ----
        try:
            name = clean_name(args.name) if args.name else ask("Name: ", clean_name)
            email = clean_email(args.email) if args.email else ask("Email: ", clean_email)
        except ValueError as error:
            print("Error:", error)
            sys.exit(1)

        # ---- the email may already be used ----
        existing = db.query(User).filter(User.email == email).first()
        if existing is not None:
            if existing.role == "Admin":
                print("\n" + email + " is already an Admin. Nothing changed.")
                return
            answer = input("\n" + email + " is already a Staff user. Make this user an Admin? [y/N]: ")
            if answer.strip().lower() == "y":
                existing.role = "Admin"
                db.commit()
                print("Done. " + email + " is now an Admin.")
            else:
                print("Nothing changed.")
            return

        # ---- password, then save ----
        password = ask_password()
        create_user(db, name, email, password, "Admin")
        print("\nAdmin account created. You can now login with " + email)

    except (KeyboardInterrupt, EOFError):
        print("\nCancelled. Nothing was saved.")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
