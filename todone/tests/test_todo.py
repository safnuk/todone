from todone import Todo

def test_class_is_importable():
    t = Todo()
    assert(type(t) == Todo)
