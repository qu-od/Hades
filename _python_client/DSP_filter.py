# written for python 3.7.2
from typing import List, Tuple, Dict, Optional, Union
from math import exp, pi, cos, sin

variant = 13
sample_rate: float = 5*(10**3) #Частота дискретизации [Гц]
band_center: float = 380
band_width: float = 20

class DifferFilter():
    def __init__(self):
        self.time_coefft: float = 0.64 #time_coefft = tau/T
        self.coeff_0: float = 1. #I meant A_coeef_0 FOR UNRECURRENT FILTER!

    def _pulse_response_coeff(self, i: int) -> float:
        if i < 1: raise ValueError("Wrong index for a coeff!")
        k = i #index
        t = self.time_coefft
        return exp(k / -t) - exp((k-1) / -t)

    def get_pulse_response_coeffs_till_N(self, N: int) -> Tuple[float]:
        coeffs: list = [self.coeff_0]
        coeffs += [self._pulse_response_coeff(i) for i in range(1, N)]
        return tuple(coeffs)

    def get_pulse_response_coeffs_with_precision(
            self, precision_rate = 0.05) -> Tuple[float]:
        coeff_1 = self._pulse_response_coeff(1)
        coeffs: list = [self.coeff_0, coeff_1]
        current_precision_rate: float = 1.
        i: int = 2
        while True: 
            current_coeff: float = self._pulse_response_coeff(i)
            current_precision_rate = current_coeff / coeff_1
            if current_precision_rate < precision_rate: break
            coeffs.append(current_coeff)
            i += 1
        return tuple(coeffs)

    def _is_feedback_needed(self) -> bool:
        return (len(self.get_pulse_response_coeffs_with_precision()) > 10)

    def get_recurrent_filter_coeffs(self) -> Tuple[Tuple[float], Tuple[float]]:
        a_coeffs = [1., -1.]
        b_coeffs = [exp(-1 / self.time_coefft)]
        return tuple(a_coeffs), tuple(b_coeffs)

    def _is_recurrent_filter_stable(self) -> bool:
        return (abs(exp(-1 / self.time_coefft)) < 1)

    def create_filter(self) -> \
            Union[Tuple[float], Tuple[Tuple[float], Tuple[float]]]:
        print("-----DIFFERENTIAL FILTER-----")
        if not self._is_feedback_needed():
            print("Creating filter with FINITE pulse response...")
            return self.get_pulse_response_coeffs_with_precision()
        if self._is_feedback_needed():
            print("Creating filter with INFINITE pulse response...")
            if self._is_recurrent_filter_stable():
                print("Recurrent filter is stable")
                return self.get_recurrent_filter_coeffs()
            elif not self._is_recurrent_filter_stable():
                print("Recurrent filter is NOT stable!")
                print("Use long a_coeffs for a unrecurrent filter instead:")
                return self.get_pulse_response_coeffs_with_precision()

    
class IntegrFilter():
    def __init__(self):
        self.time_coefft: float = 11.4 #time_coefft = tau/T
        self.coeff_0: float = 0. #I meant A_coeef_0

    def _pulse_response_coeff(self, i: int) -> float:
        if i < 1: raise ValueError("Wrong index for a coeff!")
        k = i #index
        t = self.time_coefft
        return exp(k / -t) * (exp(1 / t) - 1)

    def get_pulse_response_coeffs_till_N(self, N: int) -> Tuple[float]:
        coeffs: list = [self.coeff_0]
        coeffs += [self._pulse_response_coeff(i) for i in range(1, N)]
        return tuple(coeffs)

    def get_pulse_response_coeffs_with_precision(
            self, precision_rate = 0.05) -> Tuple[float]:
        coeff_1 = self._pulse_response_coeff(1)
        coeffs: list = [self.coeff_0, coeff_1]
        current_precision_rate: float = 1
        i: int = 2
        while True: 
            current_coeff: float = self._pulse_response_coeff(i)
            current_precision_rate = current_coeff / coeff_1
            if current_precision_rate < precision_rate: break
            coeffs.append(current_coeff)
            i += 1
        return tuple(coeffs)

    def _is_feedback_needed(self) -> bool:
        return (len(self.get_pulse_response_coeffs_with_precision()) > 10)

    def get_recurrent_filter_coeffs(self) -> Tuple[Tuple[float], Tuple[float]]:
        a_coeffs = [0., (1 - exp(-1 / self.time_coefft))]
        b_coeffs = [exp(-1 / self.time_coefft)]
        return tuple(a_coeffs), tuple(b_coeffs)

    def _is_recurrent_filter_stable(self) -> bool:
        return (abs(exp(-1 / self.time_coefft)) < 1)

    def create_filter(self) -> \
            Union[Tuple[float], Tuple[Tuple[float], Tuple[float]]]:
        print("-----INTEGRATING FILTER-----")
        if not self._is_feedback_needed():
            print("Creating filter with FINITE pulse response...")
            return self.get_pulse_response_coeffs_with_precision()
        if self._is_feedback_needed():
            print("Creating filter with INFINITE pulse response...")
            if self._is_recurrent_filter_stable():
                print("Recurrent filter is stable")
                return self.get_recurrent_filter_coeffs()
            elif not self._is_recurrent_filter_stable():
                print("Recurrent filter is NOT stable!")
                print("Use long a_coeffs for a unrecurrent filter instead:")
                return self.get_pulse_response_coeffs_with_precision()


class Resonator():
    def __init__(
            self, sample_rate: float,
            band_center: float, band_width: float):
        self.norm_phase_rate: float = 2 * pi * (band_center / sample_rate)
        self.alpha: float  = pi * (band_width / sample_rate)
        
    def create_filter(self) -> Tuple[Tuple[float], Tuple[float]]:
        print("-----RESONATOR FILTER-----")
        print("Resonator careated. Here are coeffs ((a0), (b1, b2)):")
        a0_coeff = 1
        b1_coeff = 2 * exp(-self.alpha) * cos(self.norm_phase_rate)
        b2_coeff = -exp(-2 * self.alpha)
        return a0_coeff, (b1_coeff, b2_coeff)


class ButterworthFilter():
    def __init__(self):
        self.cutoff_freq: float = 380
        self.freq_1: float = 2 * self.cutoff_freq
        self.freq_1_loss_in_decibels: float = 9

    def create_filter(self):
        pass
        print("-----BUTTERWORTH FILTER-----")

        
class BandFilter():
    def __init__(
            self, sample_rate: float,
            band_center: float, band_width: float):
        self.norm_phase_rate: float = 2 * pi * (band_center / sample_rate)
        self.norm_band_width: float = 2 * pi * (band_width / sample_rate)
        self.k1: float = -cos(self.norm_phase_rate)
        self.k2: float = \
            (1 - sin(self.norm_band_width)) / cos(self.norm_band_width)

    def create_filter(self) -> Tuple[float, float]:
        print("-----BANDSTOP FILTER-----")
        return self.k1, self.k2
        




# print(DifferFilter().get_pulse_response_coeffs_till_N(10))
# print(DifferFilter().get_pulse_response_coeffs_with_precision())
# print(DifferFilter()._is_feedback_needed())
print(DifferFilter().create_filter())

# print(IntegrFilter().get_pulse_response_coeffs_with_precision())
# print(IntegrFilter()._is_feedback_needed())
print(IntegrFilter().create_filter())

print( Resonator(sample_rate, band_center, band_width).create_filter())
print(BandFilter(sample_rate, band_center, band_width).create_filter())