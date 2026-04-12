import importlib.metadata
import torch
import torch.distributed


_original_version = importlib.metadata.version


def _patched_version(distribution_name):
    if distribution_name == "torch":
        return "2.4.0"
    return _original_version(distribution_name)


importlib.metadata.version = _patched_version


def patch_torch_xpu():
    if not hasattr(torch, 'xpu'):
        class _XpuModuleStub:
            @staticmethod
            def empty_cache():
                pass

            @staticmethod
            def is_available():
                return False

            @staticmethod
            def device_count():
                return 0

            @staticmethod
            def manual_seed(seed):
                pass

            @staticmethod
            def current_device():
                return -1

            @staticmethod
            def set_device(device):
                pass

            @staticmethod
            def synchronize(device=None):
                pass

            @staticmethod
            def reset_peak_memory_stats(device=None):
                pass

            @staticmethod
            def max_memory_allocated(device=None):
                return 0

        torch.xpu = _XpuModuleStub()


def patch_torch_mps():
    if not hasattr(torch, 'mps'):
        class _MpsModuleStub:
            @staticmethod
            def empty_cache():
                pass

            @staticmethod
            def is_available():
                return False

            @staticmethod
            def device_count():
                return 0

            @staticmethod
            def manual_seed(seed):
                pass

            @staticmethod
            def synchronize():
                pass

        torch.mps = _MpsModuleStub()


def patch_torch_distributed_device_mesh():
    if not hasattr(torch.distributed, 'device_mesh'):
        class _DeviceMeshStub:
            pass

        class _DeviceMeshModuleStub:
            DeviceMesh = _DeviceMeshStub

        torch.distributed.device_mesh = _DeviceMeshModuleStub()


def patch_torch_amp():
    if hasattr(torch, 'amp') and not hasattr(torch.amp, 'GradScaler'):
        try:
            from torch.cuda.amp import GradScaler
            torch.amp.GradScaler = GradScaler
        except ImportError:
            pass
    if hasattr(torch, 'amp') and not hasattr(torch.amp, 'autocast'):
        try:
            from torch.cuda.amp import autocast
            torch.amp.autocast = autocast
        except ImportError:
            pass


def patch_torch_dtypes():
    _dtype_fallbacks = {
        'uint16': torch.int16,
        'uint32': torch.int32,
        'uint64': torch.int64,
        'float8_e4m3fn': torch.float16,
        'float8_e5m2': torch.float16,
        'float8_e4m3fnuz': torch.float16,
        'float8_e5m2fnuz': torch.float16,
    }
    for attr, fallback in _dtype_fallbacks.items():
        if not hasattr(torch, attr):
            setattr(torch, attr, fallback)


def patch_torch_pytree():
    if hasattr(torch.utils, '_pytree'):
        pytree = torch.utils._pytree
        if not hasattr(pytree, 'register_pytree_node'):
            if hasattr(pytree, '_register_pytree_node'):
                _orig_register = pytree._register_pytree_node

                def _register_pytree_node_wrapper(cls, flatten_fn, unflatten_fn, serialized_type_name=None):
                    try:
                        _orig_register(cls, flatten_fn, unflatten_fn)
                    except TypeError:
                        _orig_register(cls, flatten_fn, unflatten_fn)

                pytree.register_pytree_node = _register_pytree_node_wrapper
            else:
                pytree.register_pytree_node = lambda *args, **kwargs: None


def check_environment():
    import warnings
    real_torch_version = _original_version("torch")
    from packaging.version import Version
    if Version(real_torch_version.split('+')[0]) < Version("2.4.0"):
        warnings.warn(
            f"\n{'='*60}\n"
            f"环境兼容性警告：当前PyTorch版本({real_torch_version})低于推荐版本(2.4.0)\n"
            f"已自动应用兼容性补丁，但可能仍存在部分功能不可用\n"
            f"建议升级PyTorch以获得最佳兼容性：\n"
            f"  CPU版: pip install torch>=2.4.0 --index-url https://download.pytorch.org/whl/cpu\n"
            f"  GPU版: pip install torch>=2.4.0 --index-url https://download.pytorch.org/whl/cu121\n"
            f"{'='*60}",
            UserWarning,
            stacklevel=2,
        )


def patch_torch_misc():
    if not hasattr(torch, 'get_default_device'):
        torch.get_default_device = lambda: torch.device('cpu')
    if not hasattr(torch, 'set_default_device'):
        torch.set_default_device = lambda device: None
    if not hasattr(torch, 'compiler'):
        torch.compiler = type('compiler', (), {'disable': lambda *a, **kw: (lambda f: f)})()


def apply_compatibility_patches():
    patch_torch_xpu()
    patch_torch_mps()
    patch_torch_distributed_device_mesh()
    patch_torch_amp()
    patch_torch_dtypes()
    patch_torch_pytree()
    patch_torch_misc()
    check_environment()


apply_compatibility_patches()
