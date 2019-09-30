def test_for_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


JUPYTER = test_for_ipython()
