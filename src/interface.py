class Interface(object):
    def __init__(self):
        pass

    def __call__(self):
        user = ''
        while user not in ['+', '-', '?', '.']:
            display(HTML(html))
            user = input(
                "Please annotate the sample above:\n"
                "[+] if the sample matches.\n"
                "[-] if the sample does not.\n"
                "[?] when unsure.\n"
                "[.] to exit (current phrase will NOT be saved).\n"
                )
            clear_output()

        if user == '.':
            return user

        self.annotations.append(
            self.Annotation(phrase, row.id, user, datetime.now())
            )
