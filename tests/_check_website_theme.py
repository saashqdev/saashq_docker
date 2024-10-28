import saashq


def check_website_theme():
    doc = saashq.new_doc("Website Theme")
    doc.theme = "test theme"
    doc.insert()


def main() -> int:
    saashq.connect(site="tests")
    check_website_theme()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
