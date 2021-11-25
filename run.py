from zentree import Interface

if __name__ == "__main__":
    import locale

    locale.setlocale(locale.LC_NUMERIC, "C")
    screen = Interface()
    screen.run()
