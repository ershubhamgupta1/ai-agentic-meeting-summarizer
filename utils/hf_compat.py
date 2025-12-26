import os
from functools import wraps

import huggingface_hub
from dotenv import load_dotenv

load_dotenv()


def patch_hf_hub_download() -> None:
    """
    This code is being used to get hugging face token from .env file and use it internally by hugging face.
    Compatibility patch for older libraries (pyannote / speechbrain)
    that still pass `use_auth_token` to hf_hub_download.
    """
    os.environ["HF_TOKEN"] = os.getenv("HUGGINGFACE_HUB_TOKEN")

    _original_hf_hub_download = huggingface_hub.hf_hub_download

    @wraps(_original_hf_hub_download)
    def _hf_hub_download_compat(*args, **kwargs):
        # pyannote passes use_auth_token, HF hub removed it
        if "use_auth_token" in kwargs and "token" not in kwargs:
            kwargs["token"] = kwargs.pop("use_auth_token")
        else:
            kwargs.pop("use_auth_token", None)
        return _original_hf_hub_download(*args, **kwargs)

    huggingface_hub.hf_hub_download = _hf_hub_download_compat
