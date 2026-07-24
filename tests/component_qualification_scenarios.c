#include "cJSON.h"
#include "cJSON_Utils.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int failures = 0;
static int scenarios = 0;
static int allocation_attempt = 0;
static int fail_after = -1;

static void *fault_malloc(size_t size)
{
    if ((fail_after >= 0) && (allocation_attempt++ >= fail_after))
    {
        return NULL;
    }
    return malloc(size);
}

static void reset_hooks(void)
{
    cJSON_InitHooks(NULL);
    fail_after = -1;
    allocation_attempt = 0;
}

static void enable_allocation_failure(int after)
{
    cJSON_Hooks hooks = { fault_malloc, free };
    allocation_attempt = 0;
    fail_after = after;
    cJSON_InitHooks(&hooks);
}

static void expect_true(const char *name, int condition)
{
    scenarios++;
    if (!condition)
    {
        fprintf(stderr, "FAIL: %s\n", name);
        failures++;
    }
}

static void expect_parse_failure(const char *name, const char *input)
{
    cJSON *parsed = cJSON_Parse(input);
    expect_true(name, parsed == NULL);
    cJSON_Delete(parsed);
}

int main(void)
{
    static const struct
    {
        const char *name;
        const char *input;
    } malformed[] = {
        {"unterminated-string", "\"unterminated"},
        {"trailing-escape", "\"\\"},
        {"lone-high-surrogate", "\"\\uD800\""},
        {"lone-low-surrogate", "\"\\uDC00\""},
        {"bad-surrogate-pair", "\"\\uD800\\u0041\""},
        {"unterminated-array", "[1,2"},
        {"array-trailing-comma", "[1,]"},
        {"unterminated-object", "{\"a\":1"},
        {"object-missing-colon", "{\"a\" 1}"},
        {"object-trailing-comma", "{\"a\":1,}"},
        {"invalid-token", "truth"},
        {"leading-plus", "+1"},
        {"empty-input", ""},
    };
    size_t index = 0;
    cJSON *from = NULL;
    cJSON *to = NULL;
    cJSON *patch = NULL;

    expect_true("version", strcmp(cJSON_Version(), "1.7.19") == 0);
    expect_true("null-string-value", cJSON_GetStringValue(NULL) == NULL);
    expect_true("null-number-is-nan", cJSON_GetNumberValue(NULL) != cJSON_GetNumberValue(NULL));
    expect_true("null-object-item", cJSON_GetObjectItemCaseSensitive(NULL, "x") == NULL);
    expect_true("null-array-size", cJSON_GetArraySize(NULL) == 0);
    expect_true("null-compare", !cJSON_Compare(NULL, NULL, 1));

    {
        cJSON *array = cJSON_CreateIntArray((const int[]){1, 3}, 2);
        cJSON *inserted = cJSON_CreateNumber(2);
        cJSON *empty_patches = cJSON_CreateArray();
        expect_true("array-created", array != NULL && inserted != NULL);
        expect_true("insert-array-middle", cJSON_InsertItemInArray(array, 1, inserted));
        expect_true("inserted-array-size", cJSON_GetArraySize(array) == 3);
        expect_true("apply-empty-patches", cJSONUtils_ApplyPatches(array, empty_patches) == 0);
        expect_true(
            "apply-empty-patches-case-sensitive",
            cJSONUtils_ApplyPatchesCaseSensitive(array, empty_patches) == 0
        );
        cJSON_Delete(empty_patches);
        cJSON_Delete(array);
    }

    for (index = 0; index < sizeof(malformed) / sizeof(malformed[0]); index++)
    {
        expect_parse_failure(malformed[index].name, malformed[index].input);
    }

    from = cJSON_Parse("{\"keep\":1,\"change\":2,\"remove\":3}");
    to = cJSON_Parse("{\"keep\":1,\"change\":4,\"add\":5}");
    patch = cJSONUtils_GenerateMergePatchCaseSensitive(from, to);
    expect_true("merge-patch-inputs", from != NULL && to != NULL);
    expect_true("merge-patch-generated", patch != NULL);
    expect_true("merge-patch-change", cJSON_GetObjectItemCaseSensitive(patch, "change") != NULL);
    expect_true("merge-patch-remove", cJSON_IsNull(cJSON_GetObjectItemCaseSensitive(patch, "remove")));
    expect_true("merge-patch-add", cJSON_GetObjectItemCaseSensitive(patch, "add") != NULL);

    for (index = 0; index < 20; index++)
    {
        cJSON *candidate = NULL;
        char *rendered = NULL;

        enable_allocation_failure((int) index);
        candidate = cJSON_Parse(
            "{\"text\":\"escaped \\\\ value\",\"array\":[1,2,3],"
            "\"nested\":{\"enabled\":true,\"none\":null}}"
        );
        cJSON_Delete(candidate);
        reset_hooks();

        enable_allocation_failure((int) index);
        rendered = cJSON_Print(from);
        cJSON_free(rendered);
        reset_hooks();

        enable_allocation_failure((int) index);
        candidate = cJSON_Duplicate(from, 1);
        cJSON_Delete(candidate);
        reset_hooks();

    }
    expect_true("allocation-fault-injection-completed", 1);

    cJSON_Delete(patch);
    cJSON_Delete(to);
    cJSON_Delete(from);

    printf("qualification scenarios: %d, failures: %d\n", scenarios, failures);
    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
