class Utils:
    @staticmethod
    def print_error_and_exit(error: str):
        print(f'[!!!ERROR!!!] {error}')
        SystemExit(1)
