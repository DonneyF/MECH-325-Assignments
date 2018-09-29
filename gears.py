import json
import math

# Gear Class. Loads JSON data and runs methods
class Gear:
    # Constants

    m_n = 1 # Load sharing ratio
    v_p = 0.3  # Poisson's Ratio for pinion
    v_g = 0.3  # Posson's Raion for gear
    load_cycles = 2E4 # Number of load cycles
    Q_v = 5 # Calculated that the maximum allowable pitch-line velocity is 3222.8 ft/min for that Q_v value.
            # Since the motor is 2500rpm, we need a circumference of the first pinion to be at least 1.289ft
            # Which is not plausible.
    motor_speed = 2500 # RPM
    motor_torque = 2.5 # Nm
    motor_torque_imp = 22.13 # Pound-inches
    R = 0.98 # Reliability factor
    overload_factor = 1

    # Constructor. Load the file
    def __init__(self):
        with open('A1_Gear_Data.json', 'r') as infile:
            self.gears = json.load(infile)

    def get_array(self):
        return self.gears

    # Retrieve a gear JSON object based on its number
    def get(self, number):
        for gear in self.gears:
            if gear["number"] == number:
                return gear

    # Update all JSON object fields if it exists
    def update_all(self, key, value):
        for gear in self.gears:
            print(gear)
            gear[key] = value

        with open('A1_Gear_Data.json', 'w') as outfile:
            json.dump(self.gears, outfile)

        with open('A1_Gear_Data.json', 'r') as infile:
            self.gears = json.load(infile)

    # Get the costs of the two gears
    def interaction_cost(self, gear1, gear2):
        return self.get(gear1)["cost"] + self.get(gear2)["cost"]

    def geometry_factor_pitting_resistance(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        m_g = gear["teeth"] / pinion["teeth"]
        phi = 20 * math.pi / 180 #Transverse pressure angle in radians
        I = (math.cos(phi) * math.sin(phi)) / (2 * self.m_n) * m_g / (m_g + 1)
        return I

    # Alternative naming
    def suface_strength_geometry(self, pinion_, gear_):
        return self.geometry_factor_pitting_resistance(pinion_, gear_)

    def elastic_coefficient(self, pinion_, gear_):
        # Table 14-8
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        # Look up table A5 for Elastic Modulus
        E_p = pinion["elastic_modulus"]
        E_g = gear["elastic_modulus"]

        C_p = math.sqrt(1 / (math.pi * ((1 - self.v_p ** 2) / (E_p) + (1 - self.v_g ** 2) / (E_g))))
        return C_p

    def surface_condition_factor(self):
        # Insufficient information to provide a proper calculation
        return 1

    def hardness_ratio_factor(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        m_g = gear["teeth"] / pinion["teeth"]

        brinell_hardness_pinion = pinion["brinell_hardness"]
        brinell_hardness_gear = gear["brinell_hardness"]

        ratio = brinell_hardness_pinion / brinell_hardness_gear

        if ratio < 1.2:
            A_ = 0
        elif ratio > 1.7:
            A_ = 0.00698
        else:
            A_ = 8.98E-3 * ratio - 8.29E-3

        C_H = 1.0 + A_ * (m_g - 1.0)
        return C_H

    def stress_cycle_factor_bending(self):
        # Approximate that all gears have the same stress cycle factor
        Y = 6.1514 * self.load_cycles ** -0.1192
        return Y

    def dynamic_factor(self, pinion1_, gear1_, pinion2_, gear2_, gear_, stage):
        pinion1 = self.get(pinion1_)
        gear1 = self.get(gear1_)

        diameter = self.get(gear_)["pitch_diameter"]
        V = 0

        omega_p1 = self.motor_speed
        omega_g1 = self.motor_speed * pinion1["teeth"] / gear1["teeth"]

        B = 0.25 * ((12 - self.Q_v) ** (2.0/3.0))
        A = 50 + 56 * (1- B)

        if pinion2_ is not None and gear2_ is not None:
            pinion2 = self.get(pinion2_)
            gear2 = self.get(gear2_)

            omega_p2 = omega_g1
            omega_g2 = self.motor_speed * pinion1["teeth"] * pinion2["teeth"] / (gear1["teeth"] * gear2["teeth"])

            if stage == 3:
                V = math.pi * diameter / 12 * omega_p2
            else:
                V = math.pi * diameter / 12* omega_g2

            k_v = ((A + math.sqrt(V)) / A) ** B
            return k_v

        if stage == 1:
            V = math.pi * diameter / 12 * omega_p1
        else:
            V = math.pi * diameter / 12 * omega_g1

        k_v = ((A + math.sqrt(V)) / A) ** B
        return k_v

    def rim_thickness_factor(self, gear_):
        if gear_ is None: return 1

        gear = self.get(gear_)

        t_r = gear["rim_thickness"]
        h_t = gear["tooth_height"]
        m_b = t_r / h_t

        if m_b < 1.2:
            return 1.6 * math.log(2.234/ m_b)
        else:
            return 1

    def load_distribution_factor(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        C_pm = 1
        C_mc = 1
        C_e = 1
        C_pf = 0

        mfw = self.min_face_width(pinion_, gear_)

        if mfw < 1:
            C_pf = mfw / (10 * pinion["pitch_diameter"]) - 0.025
        else:
            C_pf = mfw / (10 * pinion["pitch_diameter"]) - 0.0375 + 0.125 * self.min_face_width(pinion_, gear_)

        # Table 14-9 - Commercial Gearing
        A = 0.127
        B = 0.0158
        C = -0.930E-4

        C_ma = A + B * mfw + C * mfw ** 2

        K_m = 1 + C_mc * (C_pf * C_pm + C_ma * C_e)
        return K_m

    def temperature_factor(self):
        # Assume operating conditions is below 120 degrees
        return 1

    def reliability_factor(self):
        return 0.658 - 0.0759 * math.log(1 - self.R)

    def min_face_width(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)
        min_face_width = min(gear["face_width"], pinion["face_width"])
        return min_face_width

    def stress_cycle_factor_pitting_resistance(self):
        # Figure 14-15
        Z_n = 2.466 * self.load_cycles ** -0.056
        return Z_n

    def allowable_contact_stress(self, gear_):
        # Figure 14-5
        gear = self.get(gear_)
        H_b = gear["brinell_hardness"]
        S_c = 322 * H_b + 29100
        return S_c # In units of PSI

    # Alterantive name for S_c
    def surface_endurance_strength(self, gear_):
        return self.allowable_contact_stress(gear_)

    def size_factor(self, pinion_, gear_, gear_num):
        # Section 4-10
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        lewis_form_factor = pinion["lewis_form_factor"]
        pitch = pinion["pitch"]
        if gear_num == 2:
            lewis_form_factor = gear["lewis_form_factor"]
            pitch = gear["pitch"]

        K_s = 1.192 * (self.min_face_width(pinion_, gear_) * math.sqrt(lewis_form_factor) / pitch) ** 0.0535
        return K_s

    def tangential_force(self, pinion1_, gear1_, pinion2_, gear2_):
        pinion1 = self.get(pinion1_)
        gear1 = self.get(gear1_)
        torque = self.motor_torque_imp
        force = torque / (pinion1["pitch_diameter"] / 2)

        # Calculate the tangential force for the second interaction if they exist
        if pinion2_ is not None and gear2_ is not None:
            pinion2 = self.get(pinion2_)
            gear2 = self.get(gear2_)
            e = pinion1["teeth"] * pinion2["teeth"] / (gear1["teeth"] * gear2["teeth"])
            T_w = torque / e

            force = T_w / (gear2["pitch_diamter"] / 2)

        return force


    def bending_stress(self, pinion1_, gear1_, pinion2_, gear2_, stage):
        pinion1 = self.get(pinion1_)
        gear1 = self.get(gear1_)
        K_o = self.overload_factor
        sigma = 0

        if stage == 1:
            W_t = self.tangential_force(pinion1_, gear1_, None, None)
            K_v = self.dynamic_factor(pinion1_, gear1_, None, None, pinion1_, 1)
            K_s = self.size_factor(pinion1_, gear1_, 1)
            pitch = pinion1["pitch"]
            F = self.min_face_width(pinion1_, gear1_)
            K_m = self.load_distribution_factor(pinion1_, gear1_)
            K_b = self.rim_thickness_factor(pinion1_)
            J = pinion1["geometry_factor"]
            sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
        elif stage == 2:
            W_t = self.tangential_force(pinion1_, gear1_, None, None)
            K_v = self.dynamic_factor(pinion1_, gear1_, None, None, gear1_, 2)
            K_s = self.size_factor(pinion1_, gear1_, 2)
            pitch = gear1["pitch"]
            F = self.min_face_width(pinion1_, gear1_)
            K_m = self.load_distribution_factor(pinion1_, gear1_)
            K_b = self.rim_thickness_factor(gear1_)
            J = gear1["geometry_factor"]
            sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
        elif stage == 3 and pinion2_ is not None and gear2_ is not None:
            pinion2 = self.get(pinion2_)
            W_t = self.tangential_force(pinion1_, gear1_, pinion2_, gear2_)
            K_v = self.dynamic_factor(pinion1_, gear1_, pinion2_, gear2_, pinion1_, 3)
            K_s = self.size_factor(pinion2_, gear2_, 1)
            pitch = pinion2["pitch"]
            F = self.min_face_width(pinion2_, gear2_)
            K_m = self.load_distribution_factor(pinion2_, gear2_)
            K_b = self.rim_thickness_factor(pinion2_)
            J = pinion2["geometry_factor"]
            sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
        elif stage == 4 and pinion2_ is not None and gear2_ is not None:
            gear2 = self.get(gear2_)
            W_t = self.tangential_force(pinion1_, gear1_, pinion2_, gear2_)
            K_v = self.dynamic_factor(pinion1_, gear1_, pinion2_, gear2_, gear2_, 4)
            K_s = self.size_factor(pinion2_, gear2_, 2)
            pitch = gear2["pitch"]
            F = self.min_face_width(pinion2_, gear2_)
            K_m = self.load_distribution_factor(pinion2_, gear2_)
            K_b = self.rim_thickness_factor(gear2_)
            J = gear2["geometry_factor"]
            sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J

        return sigma

    def contact_stress(self, pinion1_, gear1_, pinion2_, gear2_, stage):
        pinion1 = self.get(pinion1_)
        gear1 = self.get(gear1_)
        sigma = 0
        K_o = self.overload_factor
        C_f = self.surface_condition_factor()

        if stage == 1 or stage == 2:
            W_t = self.tangential_force(pinion1_, gear1_, None, None)
            F = self.min_face_width(pinion1_, gear1_)
            K_m = self.load_distribution_factor(pinion1_, gear1_)
            C_p = self.elastic_coefficient(pinion1_, gear1_)
            I = self.geometry_factor_pitting_resistance(pinion1_, gear1_)

            d_p = pinion1["pitch_diameter"] if stage == 1 else gear1["pitch_diameter"]

            if stage == 1:
                K_v = self.dynamic_factor(pinion1_, gear1_, None, None, pinion1_, 1)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)
            elif stage == 2:
                K_v = self.dynamic_factor(pinion1_, gear1_, None, None, gear1_, 1)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)
        elif stage == 3 or stage == 4:
            pinion2 = self.get(pinion2_)
            gear2 = self.get(gear2_)
            W_t = self.tangential_force(pinion2_, gear2_, None, None)
            F = self.min_face_width(pinion2_, gear2_)
            K_m = self.load_distribution_factor(pinion2_, gear2_)
            C_p = self.elastic_coefficient(pinion2_, gear2_)
            I = self.geometry_factor_pitting_resistance(pinion2_, gear2_)

            d_p = pinion1["pitch_diameter"] if stage == 1 else gear1["pitch_diameter"]

            if stage == 1:
                K_v = self.dynamic_factor(pinion1_, gear1_, pinion2_, gear2_, gear2_, 3)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)
            elif stage == 2:
                K_v = self.dynamic_factor(pinion1_, gear1_, pinion2_, gear2_, gear2_, 4)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)

        return sigma