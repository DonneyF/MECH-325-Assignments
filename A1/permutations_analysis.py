from gears import Gear
import itertools
import datetime
import json

gears = Gear()

def compute_gear_permutation(pinion1, gear1, pinion2, gear2):
    gear_arr = [pinion1, gear1, pinion2, gear2]
    fail = False
    results = []

    # Set the output speed of the motor when subjected to the raising torque
    gears.update_torque(pinion1, gear1, pinion2, gear2)
    gears.set_speed(gears.motor_torque_raise)
    if gears.motor_speed <= 0:
        return False

    # Compute for the first gear interaction
    for i in range(0, 2):
        bending_stress = gears.bending_stress(pinion1, gear1, None, None, i + 1)
        safety_factor_bending = gears.safety_factor_bending(gear_arr[i], bending_stress)

        contact_stress = gears.contact_stress(pinion1, gear1, None, None, i + 1)
        safety_factor_contact = gears.safety_factor_contact(pinion1, gear1, contact_stress)

        if safety_factor_contact < 2.2 or safety_factor_bending < 2.2:
            fail = True
            break

        gear = {
            "role": "Pinion 1" if i is 0 else "Gear 1",
            "gear": pinion1["number"] if i is 0 else gear1["number"],
            "bending_stress": bending_stress,
            "safety_factor_bending": safety_factor_bending,
            "contact_stress": contact_stress,
            "safety_factor_contact": safety_factor_contact
        }
        results.append(gear)

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
                "role": "Pinion 2" if i is 2 else "Gear 2",
                "gear": pinion2["number"] if i is 2 else gear2["number"],
                "bending_stress": bending_stress,
                "safety_factor_bending": safety_factor_bending,
                "contact_stress": contact_stress,
                "safety_factor_contact": safety_factor_contact
            }
            results.append(gear)

    if not fail:
        if len(results) == 2:
            gears_permutation = "{}, {}".format(pinion1["number"], gear1["number"])
        else:
            gears_permutation = "{}, {}, {}, {}".format(pinion1["number"], gear1["number"], pinion2["number"], gear2["number"])

        print("Permutation: " + gears_permutation)

        for i, result in enumerate(results):
            # result = {key: format_decimal(value) for key, value in result.items()}
            if i % 2 == 0 :
                print("Pinion {}:".format(int(i / 2 + 1)))
            else:
                print("Gear {}:".format(int(i / 2 + 1)))

            print("Bending Stress: {:.4f}\nSafety Factor Bending: {:.4f} \nContact Stress: {:.4f}\nSafety Factor Contact: {:.2f}"
                 .format(result["bending_stress"], result["safety_factor_bending"],
                         result["contact_stress"], result["safety_factor_contact"]))
            print("====")

        # Get performance based on raising torque / speed
        velocity = gears.power_screw_velocity(pinion1, gear1, pinion2, gear2, 1)
        cost = gears.system_cost(pinion1, gear1, pinion2, gear2)
        performance = velocity / cost

        print("Power Screw Velocity: {:.4f}\nSystem Cost: {:.2f}\nPerformance Metric: {:.4f}".format(velocity, cost, performance))
        print("=======================\n")

        permutation = {
            "gears": gears_permutation,
            "permutation": results,
            "speed": velocity,
            "cost": cost,
            "performance": performance
        }

        return permutation

    return False

def main():
    combo = int(input("Two or Four Gear Combo? (2 or 4): ") or "2")
    log_input = input("Log output to file? (Y or N): ") or "N"

    if log_input in ("y", "Y", 'y', 'Y') :
        date_time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        log_file = open("gear_combo_" + str(combo) + "_" + date_time + ".json", "w")

    gear_numbers = [gear["number"] for gear in gears.gears]
    results = []

    if combo == 2:
        two_gear_combos = itertools.permutations(gear_numbers, 2)
        for combo in two_gear_combos:
            gear1 = gears.get(combo[0])
            gear2 = gears.get(combo[1])
            if gear1["pitch"] != gear2["pitch"]:
                continue

            permutation = compute_gear_permutation(gear1, gear2, None, None)
            if permutation is not False: results.append(permutation)

    elif combo == 4:
        # Allow for repeititions using the Cartesian product
        four_gear_combos = itertools.product(gear_numbers, repeat=4)
        for combo in four_gear_combos:
            gear1 = gears.get(combo[0])
            gear2 = gears.get(combo[1])
            gear3 = gears.get(combo[2])
            gear4 = gears.get(combo[3])
            if gear1["pitch"] != gear2["pitch"] or gear3["pitch"] != gear4["pitch"]:
                continue

            permutation = compute_gear_permutation(gear1, gear2, gear3, gear4)
            if permutation is not False: results.append(permutation)

    if log_input in ("y", "Y", 'y', 'Y') and len(results) is not 0:
        log_file.write(json.dumps(results, indent=2))
        log_file.close()

    print("Potential Gear Permutations: {}\n".format(len(results)))

    # Get maximum performance
    performances = {i["gears"] : i["performance"] for i in results}
    max_performance = max(performances.values())
    performance_combos = [i for i in performances if performances[i] == max_performance]
    print("Maximum Velocity Cobminations: {}\nPerformance Metric: {:.4f}".format(performance_combos, max_performance))

if __name__ == "__main__":
    main()