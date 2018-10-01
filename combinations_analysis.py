from gears import Gear
import itertools

gears = Gear()

def compute_gear_permutation(pinion1, gear1, pinion2, gear2):
    gear_arr = [pinion1, gear1, pinion2, gear2]
    fail = False
    results = []

    # Compute for the first gear interaction
    for i in range(0, 2):
        bending_stress = gears.bending_stress(pinion1, gear1, None, None, i + 1)
        safety_factor_bending = gears.safety_factor_bending(gear_arr[i], bending_stress)

        contact_stress = gears.contact_stress(pinion1, gear1, None, None, i + 1)
        safety_factor_contact = gears.safety_factor_contact(pinion1, gear1, contact_stress)

        if safety_factor_contact < 2.2 or safety_factor_bending < 2.2:
            failed = True
            #print("FAILED")
            break

        gear = {
            "bending_stress": bending_stress,
            "safety_factor_bending": safety_factor_bending,
            "contact_stress": contact_stress,
            "safety_factor_contact": safety_factor_contact
        }
        results.append(gear)
        # print("Gear {}:".format(i))
        # print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\n"
        #       .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact))
        # print("====")

    # Compute for the second interaction
    if pinion2 is not None and gear2 is not None:
        for i in range(2, 4):
            bending_stress = gears.bending_stress(pinion1, gear1, pinion2, gear2, i + 1)
            safety_factor_bending = gears.safety_factor_bending(gear_arr[i], bending_stress)

            contact_stress = gears.contact_stress(pinion1, gear1, pinion2, gear2, i + 1)
            safety_factor_contact = gears.safety_factor_contact(pinion2, gear2, contact_stress)

            if safety_factor_contact < 2.2 or safety_factor_bending < 2.2:
                #print("FAILED")
                fail = True
                break

            gear = {
                "bending_stress": bending_stress,
                "safety_factor_bending": safety_factor_bending,
                "contact_stress": contact_stress,
                "safety_factor_contact": safety_factor_contact
            }
            results.append(gear)
            # print("Gear {}:".format(i))
            # print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\n"
            #     .format(bending_stress, safety_factor_bending, contact_stress, safety_factor_contact))
            # print("====")

    if not fail:
        for i, result in enumerate(results):
            print("Gear: {}".format(i))
            print("Bending Stress: {}\nSafety Factor Bending: {} \nContact Stress: {}\nSafety Factor Contact: {}\n"
                 .format(result["bending_stress"], result["safety_factor_bending"], result["contact_stress"], result["safety_factor_contact"]))
            print("====")

        if len(results) == 2:
            velocity = gears.power_screw_velocity(pinion1, gear1, None, None)
            cost = gears.system_cost(pinion1, gear1, None, None)
            performance = gears.performance_metric(pinion1, gear1, None, None)
        else:
            velocity = gears.power_screw_velocity(pinion1, gear1, pinion2, gear2)
            cost = gears.system_cost(pinion1, gear1, pinion2, gear2)
            performance = gears.performance_metric(pinion1, gear1, pinion2, gear2)

        print("Power Screw Veloctity: {}\nSystem Cost: {}\nPerformance Metric: {}".format(velocity, cost, performance))
        print("=======================")

def main():
    combo = int(input("Two or Four Gear Combo? (2 or 4): "))
    gear_numbers = [gear["number"] for gear in gears.gears]

    if combo == 2:
        two_gear_combos = itertools.permutations(gear_numbers, 2)
        for combo in two_gear_combos:
            gear1 = gears.get(combo[0])
            gear2 = gears.get(combo[1])
            e = gears.train_value(gear1, gear2, None, None)

            # Minimum train value
            if e <= 1.0/4.7:
                print("Permutation: {}, {}".format(gear1["number"], gear2["number"]))
                compute_gear_permutation(gear1, gear2, None, None)

    elif combo == 4:
        four_gear_combos = itertools.permutations(gear_numbers, 4)
        for combo in four_gear_combos:
            gear1 = gears.get(combo[0])
            gear2 = gears.get(combo[1])
            gear3 = gears.get(combo[2])
            gear4 = gears.get(combo[3])
            e = gears.train_value(gear1, gear2, gear3, gear4)

            if e <= 1.0/5.0:
                print("Permutation: {}, {}, {}, {}".format(gear1["number"], gear2["number"], gear3["number"], gear4["number"]))
                compute_gear_permutation(gear1, gear2, gear3, gear4)

if __name__ == "__main__":
    main()