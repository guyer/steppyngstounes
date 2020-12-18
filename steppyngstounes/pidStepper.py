from __future__ import division
from __future__ import unicode_literals

import numpy as np

from steppyngstounes.stepper import Stepper

__all__ = ["PIDStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PIDStepper(Stepper):
    r"""Adaptive stepper using a PID controller.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = \left(\frac{e_{n-1}}{e_n}\right)^{k_P}
                      \left(\frac{1}{e_n}\right)^{k_I}
                      \left(\frac{e_{n-1}^2}{e_n e_{n-2}}\right)^{k_D}
                      \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`e_n` is the error at step :math:`n`.  :math:`k_P` is the
    proportional coefficient, :math:`k_I` is the integral coefficient, and
    :math:`k_D` is the derivative coefficient.

    On failure, retries with

    .. math::

       \Delta_n = \mathrm{min}\left(\frac{1}{e_n}, 0.8\right) \Delta_n

    Based on::

        @article{PIDpaper,
           author =  {A. M. P. Valli and G. F. Carey and A. L. G. A. Coutinho},
           title =   {Control strategies for timestep selection in finite element
                      simulation of incompressible flows and coupled
                      reaction-convection-diffusion processes},
           journal = {Int. J. Numer. Meth. Fluids},
           volume =  47,
           year =    2005,
           pages =   {201-231},
           doi =     {10.1002/fld.805},
        }

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    tryStep : float
        Suggested step size to try (default None).
    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).
    proportional : float
        PID control :math:`k_P` coefficient (default 0.075).
    integral : float
        PID control :math:`k_I` coefficient (default 0.175).
    derivative : float
        PID control :math:`k_D` coefficient (default 0.01).

    """

    __doc__ += Stepper._stepper_test.format(StepperClass="PIDStepper",
                                            args=Stepper._stepper_test_args,
                                            steps=264,
                                            attempts=281)

    def __init__(self, start, stop, tryStep=None, minStep=None,
                 inclusive=False, record=False,
                 proportional=0.075, integral=0.175, derivative=0.01):
        super(PIDStepper, self).__init__(start=start, stop=stop, tryStep=tryStep,
                                         minStep=minStep, inclusive=inclusive,
                                         record=record)

        self.proportional = proportional
        self.integral = integral
        self.derivative = derivative

        # pre-seed the error list as this algorithm needs historical errors

        # number of artificial steps needed by the algorithm
        self._needs = 3

        self._sizes *= self._needs
        self._successes *= self._needs
        self._values *= self._needs
        self._errors *= self._needs

        self._steps = list(start - np.cumsum(self._sizes)[::-1])

        self.prevStep = self.minStep

    def _shrinkStep(self):
        """Reduce step after failure

        Returns
        -------
        float
            New step.

        """
        factor = min(1. / self._errors[-1], 0.8)
        tryStep = factor * self._sizes[-1]

        self.prevStep = tryStep**2 / (self.prevStep or self.minStep)

        return tryStep

    def _adaptStep(self):
        """Calculate next step after success

        Returns
        -------
        float
            New step.

        """
        errors = np.asarray(self._errors)[self._successes]
        factor = ((errors[-2] / errors[-1])**self.proportional
                  * (1. / errors[-1])**self.integral
                  * (errors[-2]**2
                     / (errors[-1] * errors[-3]))**self.derivative)

        tryStep = factor * (self.prevStep or self._sizes[self._successes][-1])

        self.prevStep = tryStep

        return tryStep
