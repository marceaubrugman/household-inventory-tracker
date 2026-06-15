def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def get_non_negative_int(prompt):
    while True:
        raw_value = input(prompt).strip()

        try:
            value = int(raw_value)
            if value < 0:
                print("Please enter 0 or a positive number.")
            else:
                return value
        except ValueError:
            print("Please enter a valid whole number.")


def get_positive_int(prompt):
    while True:
        raw_value = input(prompt).strip()

        try:
            value = int(raw_value)
            if value <= 0:
                print("Please enter a number greater than 0.")
            else:
                return value
        except ValueError:
            print("Please enter a valid whole number.")


def get_optional_non_empty_input(prompt, current_value):
    while True:
        value = input(f"{prompt} [{current_value}]: ").strip()

        if value == "":
            return current_value
        if value:
            return value

        print("This field cannot be empty.")


def get_optional_non_negative_int(prompt, current_value):
    while True:
        raw_value = input(f"{prompt} [{current_value}]: ").strip()

        if raw_value == "":
            return current_value

        try:
            value = int(raw_value)
            if value < 0:
                print("Please enter 0 or a positive number.")
            else:
                return value
        except ValueError:
            print("Please enter a valid whole number.")


def get_positive_int_or_cancel(prompt):
    while True:
        raw_value = input(f"{prompt} (or 'q' to cancel): ").strip().lower()

        if raw_value == "q":
            return None

        try:
            value = int(raw_value)
            if value <= 0:
                print("Please enter a number greater than 0.")
            else:
                return value
        except ValueError:
            print("Please enter a valid whole number or 'q' to cancel.")