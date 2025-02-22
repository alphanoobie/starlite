from random import randint

from starlette.status import HTTP_200_OK

from starlite import Controller, MediaType, Provide, get
from starlite.testing import create_test_client


def test_inter_dependencies() -> None:
    def top_dependency(query_param: int) -> int:
        return query_param

    def mid_level_dependency() -> int:
        return 5

    def local_dependency(path_param: int, mid_level: int, top_level: int) -> int:
        return path_param + mid_level + top_level

    class MyController(Controller):
        path = "/test"
        dependencies = {"mid_level": Provide(mid_level_dependency)}

        @get(
            path="/{path_param:int}",
            dependencies={
                "summed": Provide(local_dependency),
            },
            media_type=MediaType.TEXT,
        )
        def test_function(self, summed: int) -> str:
            return str(summed)

    with create_test_client(MyController, dependencies={"top_level": Provide(top_dependency)}) as client:
        response = client.get("/test/5?query_param=5")
        assert response.text == "15"


def test_inter_dependencies_on_same_app_level() -> None:
    def first_dependency() -> int:
        return randint(1, 10)

    def second_dependency(injected_integer: int) -> bool:
        return injected_integer % 2 == 0

    @get("/true-or-false")
    def true_or_false_handler(injected_bool: bool) -> str:
        return "its true!" if injected_bool else "nope, its false..."

    with create_test_client(
        true_or_false_handler,
        dependencies={"injected_integer": Provide(first_dependency), "injected_bool": Provide(second_dependency)},
    ) as client:
        response = client.get("/true-or-false")
        assert response.status_code == HTTP_200_OK
