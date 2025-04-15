# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack import *
from spack.package import *
from spack.pkg.builtin.amr_wind import AmrWind as bAmrWind
from spack.pkg.exawind.ctest_package import *
find_machine = importlib.import_module("find-exawind-manager")

class AmrWind(bAmrWind, CtestPackage):
    version("industrial", git="https://github.com/hgopalan/amr-wind.git", branch="industrial_version", submodules=True)
    variant("asan", default=False, description="Turn on address sanitizer")
    variant("clangtidy", default=False, description="Turn on clang-tidy")

    depends_on("py-netcdf4", when="+netcdf")
    depends_on("py-numpy", when="+netcdf")

    requires("+tests", when="+cdash_submit")

    def setup_build_environment(self, env):
        spec = self.spec
        super().setup_build_environment(env)
        if spec.satisfies("+asan"):
            env.append_flags("CXXFLAGS", "-fsanitize=address -fno-omit-frame-pointer")
            env.set("LSAN_OPTIONS", "verbosity=1:log_threads=1:suppressions={0}".format(join_path(self.package_dir, "sup.asan")))

        if spec.satisfies("+cuda"):
            env.set("CUDAHOSTCXX", spack_cxx)

        machine_name, _ = find_machine.get_current_machine()
        if spec.satisfies("+gpu-aware-mpi+rocm") and machine_name == "frontier":
            env.set("MPICH_GPU_SUPPORT_ENABLED", "1")
            env.append_flags("LDFLAGS", "-I" + os.path.join(os.getenv("MPICH_DIR"), "include"))
            env.append_flags("LDFLAGS", "-L" + os.path.join(os.getenv("MPICH_DIR"), "lib"))
            env.append_flags("LDFLAGS", "-lmpi")
            env.append_flags("LDFLAGS", os.getenv("CRAY_XPMEM_POST_LINK_OPTS"))
            env.append_flags("LDFLAGS", "-lxpmem")
            env.append_flags("LDFLAGS", os.getenv("PE_MPICH_GTL_DIR_amd_gfx90a"))
            env.append_flags("LDFLAGS", os.getenv("PE_MPICH_GTL_LIBS_amd_gfx90a"))
        if spec.satisfies("+gpu-aware-mpi+cuda") and machine_name == "kestrel-gpu":
            env.set("MPICH_GPU_SUPPORT_ENABLED", "1")
            env.append_flags("CXXFLAGS", "-I" + os.path.join(os.getenv("MPICH_DIR"), "include"))
            env.append_flags("CXXFLAGS", "-L" + os.path.join(os.getenv("MPICH_DIR"), "lib"))
            env.append_flags("CXXFLAGS", "-lmpi")
            env.append_flags("CXXFLAGS", os.getenv("PE_MPICH_GTL_DIR_nvidia90"))
            env.append_flags("CXXFLAGS", os.getenv("PE_MPICH_GTL_LIBS_nvidia90"))

    def cmake_args(self):
        spec = self.spec
        cmake_options = super(AmrWind, self).cmake_args()

        if spec.satisfies("dev_path=*"):
            cmake_options.append(self.define("CMAKE_EXPORT_COMPILE_COMMANDS", True))

        if spec.satisfies("+clangtidy"):
            cmake_options.append(self.define("AMR_WIND_ENABLE_CLANG_TIDY", True))

        if spec.satisfies("+tests"):
            cmake_options.append(self.define("AMR_WIND_TEST_WITH_FCOMPARE", True))
            cmake_options.append(self.define("AMR_WIND_SAVE_GOLDS", True))
            cmake_options.append(self.define("AMR_WIND_SAVED_GOLDS_DIRECTORY", super().saved_golds_dir))
            cmake_options.append(self.define("AMR_WIND_REFERENCE_GOLDS_DIRECTORY", super().reference_golds_dir))

        if spec.satisfies("+mpi"):
            cmake_options.append(self.define("MPI_CXX_COMPILER", spec["mpi"].mpicxx))
            cmake_options.append(self.define("MPI_C_COMPILER", spec["mpi"].mpicc))

        return cmake_options
