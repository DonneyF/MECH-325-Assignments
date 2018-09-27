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
    R = 0.98 # Reliability factor

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

    def surface_strength_geometry(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        m_g = gear["teeth"] / pinion["teeth"]
        phi = 20 #Transverse pressure angle
        I = (math.cos(phi) * math.sin(phi)) / (2 * self.m_n) * m_g / (m_g + 1)

        return I

    def elastic_coefficient(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        # Look up table A5 for Elastic Modulus
        E_p = pinion["elastic_modulus"]
        E_g = gear["elastic_modulus"]

        C_p = math.sqrt(1 / (math.pi * ((1 - self.v_p ** 2) / (E_p) + (1 - self.v_g ** 2) / (E_g))))
        return C_p

    def surface_condition_factor(self):
        return 1

    def hardness_ratio_factor(self, pinion_, gear_):
        pinion = self.get(pinion_)
        gear = self.get(gear_)

        m_g = gear["teeth"] / pinion["teeth"]

        brittle_hardness_pinion = pinion["brittle_hardness"]
        brittle_hardness_gear = gear["brittle_hardness"]

        ratio = brittle_hardness_pinion / brittle_hardness_gear

        if ratio < 1.2:
            A_ = 0
        elif ratio > 1.7:
            A_ = 0.00698
        else:
            A_ = 8.98E-3 * ratio - 8.29E-3

        C_H = 1.0 + A_ * (m_g - 1.0)
        return C_H

    def stress_cycle_factor(self):
        Y = 6.1514 * self.load_cycles ** -0.1192
        return Y

    def dynamic_factor(self, pinion1_, gear1_, pinion2_, gear2_, gear_, stage):
        pinion1 = self.get(pinion1_)
        gear1 = self.get(gear1_)

        diameter = self.get(gear_)["pitch_diameter"]
        V = 0

        omega_p1 = self.motor_speed
        omega_g1 = self.motor_speed * pinion1["teeth"] / gear1["teeth"]

        B = 0.25 * ((12 - self.Q_v) ** 2.0/3.0)
        A = 50 + 56 * (1- B)

        if pinion2_ is not None and gear2_ is not None:
            pinion2 = self.get(pinion2_)
            gear2 = self.get(gear2_)

            omega_p2 = omega_g1
            omega_g2 = self.motor_speed * pinion1["teeth"] * pinion2["teeth"] / (gear1["teeth"] * gear2["teeth"])

            if stage == 3:
                V = math.pi * diameter * omega_p2
            else:
                V = math.pi * diameter * omega_g2

            k_v = ((A + math.sqrt(V)) / A) ** B
            return k_v

        if stage == 1:
            V = math.pi * diameter * omega_p1
        else:
            V = math.pi * diameter * omega_g1

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

        min_face_width = min(gear["teeth_width"], pinion["teeth_width"])

        if min_face_width < 1:
            C_pf = min_face_width / (10 * pinion["pitch_diameter"]) - 0.025
        else:
            C_pf = min_face_width / (10 * pinion["pitch_diameter"]) - 0.0375 + 0.125 * min_face_width

        # Table 14-9 - Commercial Gearing
        A = 0.127
        B = 0.0158
        C = -0.930E-4

        C_ma = A + B * min_face_width + C * min_face_width ** 2

        K_m = 1 + C_mc * (C_pf * C_pm + C_ma * C_e)
        return K_m

    def temperature_factor(self):
        return 1

    def reliability_factor(self):
        return 0.658 - 0.0759 * math.log(1 - self.R)