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