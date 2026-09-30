load("//third_party/bazel_rules/rules_python/python:defs.bzl", "py_binary", "py_library")
load("//third_party/py/pytest:pytest_defs.bzl", "pytest_test")

package(
    default_applicable_licenses = ["//third_party/py/google/adk:package_license"],
    default_visibility = ["//visibility:public"],
)

licenses(["notice"])

py_library(
    name = "bakeoff_lib",
    srcs = glob(["src/bakeoff/**/*.py"]),
    data = glob([
        "src/bakeoff/prompts/*.md",
        "eval/golden/*.json",
        "examples/sample_corpus/*.json",
    ]),
    imports = ["src"],
    deps = [
        "//third_party/py/google/cloud:core",
        "//third_party/py/google/cloud/secretmanager",
        "//third_party/py/httpx",
        "//third_party/py/opentelemetry:opentelemetry_api",
        "//third_party/py/opentelemetry:opentelemetry_sdk",
        "//third_party/py/pydantic:pydantic_v2",
        "//third_party/py/structlog",
    ],
)

py_binary(
    name = "demo",
    srcs = ["examples/run_bakeoff_demo.py"],
    data = glob([
        "src/bakeoff/prompts/*.md",
        "examples/sample_corpus/*.json",
    ]),
    main = "examples/run_bakeoff_demo.py",
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_schemas",
    srcs = ["tests/test_schemas.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_tools",
    srcs = ["tests/test_tools.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_memory",
    srcs = ["tests/test_memory.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_observability",
    srcs = ["tests/test_observability.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_guardrails",
    srcs = ["tests/test_guardrails.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_pipeline_integration",
    srcs = ["tests/test_pipeline_integration.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_trajectory",
    srcs = ["eval/test_trajectory.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_judge_stability",
    srcs = ["eval/test_judge_stability.py"],
    deps = [
        ":bakeoff_lib",
    ],
)

pytest_test(
    name = "test_bias_regression",
    srcs = ["eval/test_bias_regression.py"],
    deps = [
        ":bakeoff_lib",
    ],
)
