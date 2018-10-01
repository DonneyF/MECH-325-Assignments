from gears import Gear
import itertools

gears = Gear()

def compute_gear_combination(pinion1, gear1, pinion2, gear2):
    gear_arr = [pinion1, gear1, pinion2, gear2]

    num_gears = 2 if pinion2 is None or gear2 is None else 4

    for i in range(0, num_gears):
        print("Gear {}:\n".format(i))
        bending_stress = gears.bending_stress(pinion1, gear1, pinion2, gear2, i + 1)
        safety_factor_bending = gears.safety_factor_bending(gear_arr[i - 1], bending_stress)

        contact_stress = gears.contact_stress(pinion1, gear1, pinion2, gear2, i + 1)
        safety_factor_contact = gears.safety_factor_contact(gear_arr[i], gear_arr[i + 1], contact_stress)
        cost = gears.interaction_cost(gear_arr[i], gear_arr[i + 1])

        print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\n"
              .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact,cost))

        if num_gears <= 2:
            cost = gears.interaction_cost(gear_arr[0], gear_arr[1])
        else:
            cost = gears.interaction_cost(gear_arr[0], gear_arr[1]) + gears.interaction_cost(gear_arr[2], gear_arr[3])

        print("Cost: {}".format(cost))
        print("=======================")

gear_numbers = [gear["number"] for gear in gears.gears]

two_gear_combos = itertools.combinations(gear_numbers, 2)
four_gear_combos = itertools.combinations(gear_numbers, 4)

for combo in two_gear_combos:
    gear1 = gears.get(combo[0])
    gear2 = gears.get(combo[1])
    e = gears.train_value(gear1, gear2, None, None)
    if e <= 1.0/4.7:
        compute_gear_combination(gear1, gear2, None, None)
