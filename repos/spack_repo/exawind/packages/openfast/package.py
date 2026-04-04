# Copyright (c) 2022, National Technology & Engineering Solutions of Sandia,
# LLC (NTESS). Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.
#
# This software is released under the BSD 3-clause license. See LICENSE file
# for more details.

from spack.package import *
from spack_repo.builtin.packages.openfast.package import Openfast as bOpenfast


class Openfast(bOpenfast):

    def patch(self):
        # Fix Fortran standard violation in TSsubs.f90: the OMP THREADPRIVATE
        # directive for TRH appears before TRH is declared, which is rejected
        # by strict Fortran compilers (e.g. AOCC/Flang). Swap the declaration
        # and the directive so the declaration comes first.
        # Upstream issue: OpenFAST 4.2.0, modules/turbsim/src/TSsubs.f90
        if self.spec.satisfies("@4.2.0"):
            fname = 'modules/turbsim/src/TSsubs.f90'
            with open(fname, 'r') as f:
                lines = f.readlines()
            for i in range(len(lines) - 1):
                if ('THREADPRIVATE(TRH)' in lines[i] and
                        'allocatable' in lines[i + 1] and 'TRH' in lines[i + 1]):
                    lines[i], lines[i + 1] = lines[i + 1], lines[i]
                    break
            with open(fname, 'w') as f:
                f.writelines(lines)
