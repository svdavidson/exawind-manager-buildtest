from spack_repo.builtin.packages.rosco.package import Rosco as BuiltinRosco

from spack.package import *


class Rosco(BuiltinRosco):
    # Fix backslash line continuation (gfortran extension) to standard & for flang compatibility
    patch("flang-backslash.patch", when="@main %aocc")
