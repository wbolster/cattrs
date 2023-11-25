from typing import List, Optional

from attrs import define
from attrs import fields as f
from pytest import raises

from cattrs import BaseConverter
from cattrs.errors import ClassValidationError
from cattrs.v import (
    V,
    between,
    customize,
    greater_than,
    ignoring_none,
    is_unique,
    len_between,
    transform_error,
)


@define
class WithInt:
    a: int


@define
class WithList:
    a: List[int]


@define
class WithOptional:
    a: Optional[int]


def test_gt(converter: BaseConverter):
    """The greater_than validator works."""
    customize(converter, WithInt, V(f(WithInt).a).ensure(greater_than(10)))

    assert converter.structure({"a": 11}, WithInt) == WithInt(11)

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": 10}, WithInt)

        assert transform_error(exc_info.value) == [
            "invalid value (10 not greater than 10) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": 10}, WithInt)

        assert repr(exc_info.value) == "ValueError('10 not greater than 10')"


def test_between(converter: BaseConverter):
    """The between validator works."""
    customize(converter, WithInt, V(f(WithInt).a).ensure(between(10, 20)))

    assert converter.structure({"a": 10}, WithInt) == WithInt(10)
    assert converter.structure({"a": 19}, WithInt) == WithInt(19)

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": 9}, WithInt)

        assert transform_error(exc_info.value) == [
            "invalid value (9 not between 10 and 20) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": 9}, WithInt)

        assert repr(exc_info.value) == "ValueError('9 not between 10 and 20')"

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": 20}, WithInt)

        assert transform_error(exc_info.value) == [
            "invalid value (20 not between 10 and 20) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": 20}, WithInt)

        assert repr(exc_info.value) == "ValueError('20 not between 10 and 20')"


def test_len_between(converter: BaseConverter):
    """The len_between validator works."""
    customize(converter, WithList, V(f(WithList).a).ensure(len_between(1, 2)))

    assert converter.structure({"a": [1]}, WithList) == WithList([1])

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": []}, WithList)

        assert transform_error(exc_info.value) == [
            "invalid value (length (0) not between 1 and 2) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": []}, WithList)

        assert repr(exc_info.value) == "ValueError('length (0) not between 1 and 2')"

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": [1, 2]}, WithList)

        assert transform_error(exc_info.value) == [
            "invalid value (length (2) not between 1 and 2) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": [1, 2]}, WithList)

        assert repr(exc_info.value) == "ValueError('length (2) not between 1 and 2')"


def test_unique(converter: BaseConverter):
    """The `is_unique` validator works."""

    customize(converter, WithList, V(f(WithList).a).ensure(is_unique))

    assert converter.structure({"a": [1]}, WithList) == WithList([1])

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": [1, 1]}, WithList)

        assert transform_error(exc_info.value) == [
            "invalid value (Collection (2 elem(s)) not unique, only 1 unique elem(s)) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": [1, 1]}, WithList)

        assert (
            repr(exc_info.value)
            == "ValueError('Collection (2 elem(s)) not unique, only 1 unique elem(s)')"
        )


def test_ignoring_none(converter: BaseConverter):
    """`ignoring_none` works."""

    customize(
        converter,
        WithOptional,
        V(f(WithOptional).a).ensure(ignoring_none(between(0, 5))),
    )

    assert converter.structure({"a": None}, WithOptional) == WithOptional(None)
    assert converter.structure({"a": 1}, WithOptional) == WithOptional(1)

    if converter.detailed_validation:
        with raises(ClassValidationError) as exc_info:
            converter.structure({"a": 10}, WithOptional)

        assert transform_error(exc_info.value) == [
            "invalid value (10 not between 0 and 5) @ $.a"
        ]
    else:
        with raises(ValueError) as exc_info:
            converter.structure({"a": 10}, WithOptional)

        # assert repr(exc_info.value) == "invalid value (10 not between 0 and 5) @ $.a"