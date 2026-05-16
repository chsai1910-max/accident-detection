
import sys

try:
    import pyds

    REQUIRED = [
        "NvDsFrameMeta",
        "NvDsObjectMeta",
        "gst_buffer_get_nvds_batch_meta"
    ]

    missing = []

    for r in REQUIRED:
        if not hasattr(pyds, r):
            missing.append(r)

    if missing:
        raise RuntimeError(
            f"Invalid DeepStream pyds binding. Missing: {missing}"
        )

    print("DeepStream bindings verified successfully")

except Exception as e:
    print("ERROR:")
    print(e)
    sys.exit(1)
