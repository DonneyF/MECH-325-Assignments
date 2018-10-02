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
    raising_torque = 79.5499 # Nm
    lowering_torque = 32.4104 # Nm
    motor_torque_raise = 0  # Pound-inches
    motor_torque_lower = 0  # Pound-inches
    motor_torque_imp_raise = 0 # Pound-inches
    motor_torque_imp_lower = 0 # Pound-inches
    R = 0.98 # Reliability factor
    reliability_factor = 0.658 - 0.0759 * math.log(1 - R)
    overload_factor = 1.25
    temperature_factor = 1
    worm_power_screw_ratio = 1.0/9.0
    power_screw_pitch = 6 # In mm
    motor_operation_cost = 0.30 # Dollars per hour
    stroke_length = 30 # in cm (raise only)
    worm_efficiency = 0.8034
    gear_efficiency = 0.94

    # Determines the torque subjected to the motor and updates the internal value
    def update_torque(self, pinion1, gear1, pinion2, gear2):
        e = self.train_value(pinion1, gear1, pinion2, gear2)
        eff = self.worm_efficiency * self.gear_efficiency
        self.motor_torque_raise = self.raising_torque * e * self.worm_power_screw_ratio / eff
        self.motor_torque_lower = self.lowering_torque * e * self.worm_power_screw_ratio / eff
        self.motor_torque_imp_raise = self.raising_torque * e * self.worm_power_screw_ratio * 8.8507457673787 / (.94 * .8) # Convert to pound-inches
        self.motor_torque_imp_lower = self.lowering_torque * e * self.worm_power_screw_ratio * 8.8507457673787 / (.94 * .8)  # Convert to pound-inches

    def set_speed(self, torque):
        speed = (torque - 5) * -1000
        self.motor_speed = speed

    # Constructor. Load the file
    def __init__(self):
        with open('A1_Gear_Data.json', 'r') as infile:
            self.gears = json.load(infile)

    # Retrieve a gear JSON object based on its number
    def get(self, number):
        for gear in self.gears:
            if gear["number"] == number:
                return gear

    # Update all JSON object fields if it exists
    def update_all(self, key, value):
        for gear in self.gears:
            gear[key] = value

        with open('A1_Gear_Data.json', 'w') as outfile:
            json.dump(self.gears, outfile)

        with open('A1_Gear_Data.json', 'r') as infile:
            self.gears = json.load(infile)

    # Get the costs of the two gears
    def interaction_cost(self, gear1, gear2):
        if gear1 is None or gear2 is None:
            return 0
        return gear1["cost"] + gear2["cost"]

    def geometry_factor_pitting_resistance(self, pinion, gear):

        m_g = gear["teeth"] / pinion["teeth"]
        phi = 20 * math.pi / 180 #Transverse pressure angle in radians
        I = (math.cos(phi) * math.sin(phi)) / (2 * self.m_n) * m_g / (m_g + 1)
        return I

    # Alternative naming
    def suface_strength_geometry(self, pinion, gear):
        return self.geometry_factor_pitting_resistance(pinion, gear)

    def elastic_coefficient(self, pinion, gear):
        # Table 14-8
        # Look up table A5 for Elastic Modulus
        E_p = pinion["elastic_modulus"]
        E_g = gear["elastic_modulus"]

        C_p = math.sqrt(1 / (math.pi * ((1 - self.v_p ** 2) / (E_p) + (1 - self.v_g ** 2) / (E_g))))
        return C_p

    def surface_condition_factor(self):
        # Insufficient information to provide a proper calculation
        return 1

    def hardness_ratio_factor(self, pinion, gear):
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

    def dynamic_factor(self, pinion1, gear1, pinion2, gear2, gear, stage):
        # Set speed of motor to raise to get max dynamic factor
        self.set_speed(self.motor_torque_raise)
        diameter = gear["pitch_diameter"]
        V = 0

        omega_p1 = self.motor_speed
        omega_g1 = self.motor_speed * pinion1["teeth"] / gear1["teeth"]

        B = 0.25 * ((12 - self.Q_v) ** (2.0/3.0))
        A = 50 + 56 * (1- B)

        if pinion2 is not None and gear2 is not None:
            omega_p2 = omega_g1
            omega_g2 = self.motor_speed * self.train_value(pinion1, gear1, pinion2, gear2)

            if stage == 3:
                V = math.pi * diameter / 12 * omega_p2
            else:
                V = math.pi * diameter / 12 * omega_g2

            k_v = ((A + math.sqrt(V)) / A) ** B
            return k_v

        if stage == 1:
            V = math.pi * diameter / 12 * omega_p1
        else:
            V = math.pi * diameter / 12 * omega_g1

        k_v = ((A + math.sqrt(V)) / A) ** B
        return k_v

    def rim_thickness_factor(self, gear):
        if gear is None: return 1

        t_r = gear["rim_thickness"]
        h_t = gear["tooth_height"]
        m_b = t_r / h_t

        if m_b < 1.2:
            return 1.6 * math.log(2.234/ m_b)
        else:
            return 1

    def load_distribution_factor(self, pinion, gear):
        C_pm = 1
        C_mc = 1
        C_e = 1
        C_pf = 0

        mfw = self.min_face_width(pinion, gear)

        if mfw < 1:
            C_pf = mfw / (10 * pinion["pitch_diameter"]) - 0.025
        else:
            C_pf = mfw / (10 * pinion["pitch_diameter"]) - 0.0375 + 0.125 * self.min_face_width(pinion, gear)

        # Table 14-9 - Commercial Gearing
        A = 0.127
        B = 0.0158
        C = -0.930E-4

        C_ma = A + B * mfw + C * mfw ** 2

        K_m = 1 + C_mc * (C_pf * C_pm + C_ma * C_e)
        return K_m

    def min_face_width(self, pinion, gear):
        min_face_width = min(gear["face_width"], pinion["face_width"])
        return min_face_width

    def stress_cycle_factor_pitting_resistance(self):
        # Figure 14-15
        Z_n = 2.466 * self.load_cycles ** -0.056
        return Z_n

    def allowable_contact_stress(self, gear):
        # Figure 14-5
        H_b = gear["brinell_hardness"]
        S_c = 322 * H_b + 29100
        return S_c # In units of PSI

    def allowable_bending_stress(self, gear):
        # Figure 14-2
        H_b = gear["brinell_hardness"]
        S_t = 77.3 * H_b + 12800
        return S_t

    def train_value(self, pinion1, gear1, pinion2, gear2):
        e  = pinion1["teeth"] / gear1["teeth"]
        if pinion2 is not None and gear2 is not None:
            e = pinion1["teeth"] * pinion2["teeth"] / (gear1["teeth"] * gear2["teeth"])

        return e

    # Alterantive name for S_c
    def surface_endurance_strength(self, gear):
        return self.allowable_contact_stress(gear)

    def size_factor(self, pinion, gear, gearnum):
        # Section 4-10
        lewis_form_factor = pinion["lewis_form_factor"]
        pitch = pinion["pitch"]
        if gearnum == 2:
            lewis_form_factor = gear["lewis_form_factor"]
            pitch = gear["pitch"]

        K_s = 1.192 * (self.min_face_width(pinion, gear) * math.sqrt(lewis_form_factor) / pitch) ** 0.0535
        return K_s

    def tangential_force(self, pinion1, gear1, pinion2, gear2):
        torque = self.motor_torque_imp_raise
        force = torque / (pinion1["pitch_diameter"] / 2)

        # Calculate the tangential force for the second interaction if they exist
        if pinion2 is not None and gear2 is not None:
            e = self.train_value(pinion1, gear1, pinion2, gear2)
            T_w = torque / e

            force = T_w / (gear2["pitch_diameter"] / 2)

        return force


    def bending_stress(self, pinion1, gear1, pinion2, gear2, stage):
        K_o = self.overload_factor
        sigma = 0

        if stage == 1 or stage == 2:
            W_t = self.tangential_force(pinion1, gear1, None, None)
            F = self.min_face_width(pinion1, gear1)
            K_m = self.load_distribution_factor(pinion1, gear1)

            pitch = pinion1["pitch"] if stage == 1 else gear1["pitch"]
            J = pinion1["geometry_factor"] if stage == 1 else gear1["geometry_factor"]

            if stage == 1:
                K_v = self.dynamic_factor(pinion1, gear1, None, None, pinion1, 1)
                K_s = self.size_factor(pinion1, gear1, 1)
                K_b = self.rim_thickness_factor(pinion1)
                sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
            elif stage == 2:
                K_v = self.dynamic_factor(pinion1, gear1, None, None, gear1, 2)
                K_s = self.size_factor(pinion1, gear1, 2)
                K_b = self.rim_thickness_factor(gear1)
                sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
        elif stage == 3 or stage == 4:
            W_t = self.tangential_force(pinion1, gear1, pinion2, gear2)
            F = self.min_face_width(pinion2, gear2)
            K_m = self.load_distribution_factor(pinion2, gear2)

            pitch = pinion2["pitch"] if stage == 3 else gear2["pitch"]
            J = pinion2["geometry_factor"] if stage == 3 else gear2["geometry_factor"]

            if stage == 3:
                K_v = self.dynamic_factor(pinion1, gear1, pinion2, gear2, pinion1, 3)
                K_s = self.size_factor(pinion2, gear2, 1)
                K_b = self.rim_thickness_factor(pinion2)
                sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J
            elif stage == 4:
                K_v = self.dynamic_factor(pinion1, gear1, pinion2, gear2, gear2, 4)
                K_s = self.size_factor(pinion2, gear2, 2)
                K_b = self.rim_thickness_factor(gear2)
                sigma = W_t * K_o * K_v * K_s * pitch / F * K_m * K_b / J

        return sigma

    def contact_stress(self, pinion1, gear1, pinion2, gear2, stage):
        sigma = 0
        K_o = self.overload_factor
        C_f = self.surface_condition_factor()

        if stage == 1 or stage == 2:
            W_t = self.tangential_force(pinion1, gear1, None, None)
            F = self.min_face_width(pinion1, gear1)
            K_m = self.load_distribution_factor(pinion1, gear1)
            C_p = self.elastic_coefficient(pinion1, gear1)
            I = self.geometry_factor_pitting_resistance(pinion1, gear1)

            d_p = pinion1["pitch_diameter"] if stage == 1 else gear1["pitch_diameter"]

            if stage == 1:
                K_s = self.size_factor(pinion1, gear1, 1)
                K_v = self.dynamic_factor(pinion1, gear1, None, None, pinion1, 1)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_s * K_m / d_p / F * C_f / I)
            elif stage == 2:
                K_s = self.size_factor(pinion1, gear1, 2)
                K_v = self.dynamic_factor(pinion1, gear1, None, None, gear1, 2)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_s * K_m / d_p / F * C_f / I)
        elif stage == 3 or stage == 4:
            W_t = self.tangential_force(pinion2, gear2, None, None)
            F = self.min_face_width(pinion2, gear2)
            K_m = self.load_distribution_factor(pinion2, gear2)
            C_p = self.elastic_coefficient(pinion2, gear2)
            I = self.geometry_factor_pitting_resistance(pinion2, gear2)

            d_p = pinion1["pitch_diameter"] if stage == 1 else gear1["pitch_diameter"]

            if stage == 3:
                K_v = self.dynamic_factor(pinion1, gear1, pinion2, gear2, gear2, 3)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)
            elif stage == 4:
                K_v = self.dynamic_factor(pinion1, gear1, pinion2, gear2, gear2, 4)
                sigma = C_p * math.sqrt(W_t * K_o * K_v * K_m / d_p / F * C_f / I)

        return sigma

    def safety_factor_bending(self, gear, bending_stress):
        S_t = self.allowable_bending_stress(gear)
        Y_n = self.stress_cycle_factor_bending()
        K_t = self.temperature_factor
        K_r = self.reliability_factor

        S_f = S_t * Y_n / (K_t * K_r * bending_stress)
        return S_f

    def safety_factor_contact(self, pinion, gear, contact_stress):
        S_c = self.allowable_contact_stress(gear)
        Z_n = self.stress_cycle_factor_pitting_resistance()
        C_h = self.hardness_ratio_factor(pinion, gear)
        K_t = self.temperature_factor
        K_r = self.reliability_factor

        S_h = S_c * Z_n * C_h / (K_t * K_r * contact_stress)
        return S_h

    def power_screw_velocity(self, pinion1, gear1, pinion2, gear2, raise_load):
        e = self.train_value(pinion1, gear1, None, None)

        if pinion2 is not None and gear2 is not None:
            e = self.train_value(pinion1, gear1, pinion2, gear2)

        if raise_load == 1:
            self.set_speed(self.motor_torque_raise)
        else:
            self.set_speed(self.motor_torque_lower)

        omega_motor = self.motor_speed * 2 * math.pi / 60.0
        omega_worm = e * omega_motor
        omega_screw = omega_worm * self.worm_power_screw_ratio
        screw_speed = omega_screw / (2 * math.pi) * self.power_screw_pitch
        return screw_speed # In mm/s

    def system_cost(self, pinion1, gear1, pinion2, gear2):
        material_cost = self.interaction_cost(pinion1, gear1) + self.interaction_cost(pinion2, gear2)

        # Raising cost
        speed = self.power_screw_velocity(pinion1, gear1, pinion2, gear2, 1)
        seconds_per_stroke = self.stroke_length * 10 / speed
        #print("Raising Cycle: {}".format(seconds_per_stroke))
        #print("Raising speed: {}".format(speed))
        operation_cost_raise = seconds_per_stroke * self.load_cycles / 3600 * self.motor_operation_cost

        # Lowering torque
        speed = self.power_screw_velocity(pinion1, gear1, pinion2, gear2, 2)
        seconds_per_stroke = self.stroke_length * 10 / speed
        #print("Lowering Cycle: {}".format(seconds_per_stroke))
        #print("Lowering speed: {}".format(speed))
        operation_cost_lower = seconds_per_stroke * self.load_cycles / 3600 * self.motor_operation_cost

        #print("Material Cost: {}".format(material_cost))
        return material_cost + operation_cost_raise + operation_cost_lower

    # Get the performance metric
    def performance_metric(self, pinion1, gear1, pinion2, gear2):

        speed = self.power_screw_velocity(pinion1, gear1, pinion2, gear2, 1)
        cost = self.system_cost(pinion1, gear1, pinion2, gear2)

        return speed / cost
