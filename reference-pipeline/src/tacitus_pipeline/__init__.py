"""Read-only reference pipeline. Authored interpretations remain proposed."""
from .core import PipelineError, build, load_collection, write_bundle
__all__ = ["PipelineError", "build", "load_collection", "write_bundle"]
__version__ = "0.1.0"
